import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from app.redis_client import redis_client


@dataclass
class RefreshTokenMeta:
    user_id: uuid.UUID
    expires_at: datetime
    revoked: bool


def _token_key(token: str) -> str:
    return f"rt:{token}"


def _revoked_key(token: str) -> str:
    return f"rt:revoked:{token}"


def _user_key(user_id: uuid.UUID) -> str:
    return f"rt:user:{user_id}"


def _encode_value(user_id: uuid.UUID, expires_at: datetime) -> str:
    return f"{user_id}|{expires_at.isoformat()}"


def _decode_value(raw: str) -> tuple[uuid.UUID, datetime]:
    uid_str, exp_str = raw.split("|", 1)
    return uuid.UUID(uid_str), datetime.fromisoformat(exp_str)


def _ttl_seconds(expires_at: datetime) -> int:
    return max(0, int((expires_at - datetime.now(timezone.utc)).total_seconds()))


class RefreshTokenDAO:

    async def create(self, user_id: uuid.UUID, token: str, expires_at: datetime) -> None:
        """存储新的 refresh token，TTL 自动跟随过期时间"""
        ttl = _ttl_seconds(expires_at)
        if ttl <= 0:
            return
        await redis_client.set(_token_key(token), _encode_value(user_id, expires_at), ex=ttl)
        await redis_client.sadd(_user_key(user_id), token)

    async def get_by_token(self, token: str) -> RefreshTokenMeta | None:
        """
        查找 token 元数据。
        - 活跃 token → revoked=False
        - 已吊销 token（仍在原始 TTL 内）→ revoked=True（用于盗用检测）
        - 不存在或已过期 → None
        """
        raw = await redis_client.get(_token_key(token))
        if raw:
            uid, exp = _decode_value(raw)
            return RefreshTokenMeta(user_id=uid, expires_at=exp, revoked=False)

        raw = await redis_client.get(_revoked_key(token))
        if raw:
            uid, exp = _decode_value(raw)
            return RefreshTokenMeta(user_id=uid, expires_at=exp, revoked=True)

        return None

    async def revoke(self, token: str) -> bool:
        """
        吊销指定的 refresh token：
        1. 从活跃存储中删除
        2. 写入吊销集合（保留剩余 TTL，用于后续盗用检测）
        3. 从用户活跃 token 集合中移除
        """
        raw = await redis_client.get(_token_key(token))
        if not raw:
            return False

        await redis_client.delete(_token_key(token))

        _, expires_at = _decode_value(raw)
        remaining_ttl = _ttl_seconds(expires_at)
        if remaining_ttl > 0:
            await redis_client.set(_revoked_key(token), raw, ex=remaining_ttl)

        uid_str = raw.split("|", 1)[0]
        await redis_client.srem(_user_key(uuid.UUID(uid_str)), token)
        return True

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> int:
        """
        吊销该用户的所有活跃 refresh token（用于登出/盗用检测）。
        将每个 token 移入吊销集合以保留盗用检测能力。
        """
        ukey = _user_key(user_id)
        tokens = await redis_client.smembers(ukey)
        count = 0
        for token in tokens:
            raw = await redis_client.get(_token_key(token))
            if raw:
                await redis_client.delete(_token_key(token))
                _, expires_at = _decode_value(raw)
                remaining_ttl = _ttl_seconds(expires_at)
                if remaining_ttl > 0:
                    await redis_client.set(_revoked_key(token), raw, ex=remaining_ttl)
                count += 1
        if tokens:
            await redis_client.delete(ukey)
        return count

    async def cleanup_expired(self, user_id: uuid.UUID) -> int:
        """
        清理用户 token 集合中已过期的引用。
        实际 token 数据由 Redis TTL 自动清除，此方法仅维护集合一致性。
        """
        ukey = _user_key(user_id)
        tokens = await redis_client.smembers(ukey)
        stale: list[str] = []
        for token in tokens:
            if not await redis_client.exists(_token_key(token)):
                stale.append(token)
        if stale:
            await redis_client.srem(ukey, *stale)
        return len(stale)
