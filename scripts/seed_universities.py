"""种子数据：985/211/双一流院校基础信息"""
import asyncio
import uuid
import sys
sys.path.insert(0, "backend")

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session
from app.models.university import University

# 部分985院校示例数据（实际需3000+条）
UNIVERSITIES = [
    {"name": "清华大学", "province": "北京", "city": "北京", "level": "985", "type": "理工",
     "tags": ["985", "211", "双一流", "C9"], "tuition_min": 5000, "tuition_max": 10000,
     "website": "https://www.tsinghua.edu.cn", "latitude": 39.9994, "longitude": 116.3267},
    {"name": "北京大学", "province": "北京", "city": "北京", "level": "985", "type": "综合",
     "tags": ["985", "211", "双一流", "C9"], "tuition_min": 5000, "tuition_max": 8000,
     "website": "https://www.pku.edu.cn", "latitude": 39.9870, "longitude": 116.3052},
    {"name": "浙江大学", "province": "浙江", "city": "杭州", "level": "985", "type": "综合",
     "tags": ["985", "211", "双一流", "C9"], "tuition_min": 5500, "tuition_max": 9000,
     "website": "https://www.zju.edu.cn", "latitude": 30.3085, "longitude": 120.0864},
    {"name": "复旦大学", "province": "上海", "city": "上海", "level": "985", "type": "综合",
     "tags": ["985", "211", "双一流"], "tuition_min": 5500, "tuition_max": 8500,
     "website": "https://www.fudan.edu.cn", "latitude": 31.2986, "longitude": 121.5034},
    {"name": "上海交通大学", "province": "上海", "city": "上海", "level": "985", "type": "理工",
     "tags": ["985", "211", "双一流", "C9"], "tuition_min": 5500, "tuition_max": 9000,
     "website": "https://www.sjtu.edu.cn", "latitude": 31.0282, "longitude": 121.4436},
    {"name": "华中科技大学", "province": "湖北", "city": "武汉", "level": "985", "type": "理工",
     "tags": ["985", "211", "双一流"], "tuition_min": 4500, "tuition_max": 8000,
     "website": "https://www.hust.edu.cn", "latitude": 30.5115, "longitude": 114.4143},
    {"name": "武汉大学", "province": "湖北", "city": "武汉", "level": "985", "type": "综合",
     "tags": ["985", "211", "双一流"], "tuition_min": 4500, "tuition_max": 8000,
     "website": "https://www.whu.edu.cn", "latitude": 30.5378, "longitude": 114.3626},
    {"name": "南京大学", "province": "江苏", "city": "南京", "level": "985", "type": "综合",
     "tags": ["985", "211", "双一流", "C9"], "tuition_min": 5200, "tuition_max": 7800,
     "website": "https://www.nju.edu.cn", "latitude": 32.0579, "longitude": 118.7781},
    {"name": "中国科学技术大学", "province": "安徽", "city": "合肥", "level": "985", "type": "理工",
     "tags": ["985", "211", "双一流", "C9"], "tuition_min": 4800, "tuition_max": 7000,
     "website": "https://www.ustc.edu.cn", "latitude": 31.8427, "longitude": 117.2654},
    {"name": "西安交通大学", "province": "陕西", "city": "西安", "level": "985", "type": "理工",
     "tags": ["985", "211", "双一流", "C9"], "tuition_min": 4500, "tuition_max": 7500,
     "website": "https://www.xjtu.edu.cn", "latitude": 34.2358, "longitude": 108.9872},
    {"name": "哈尔滨工业大学", "province": "黑龙江", "city": "哈尔滨", "level": "985", "type": "理工",
     "tags": ["985", "211", "双一流", "C9"], "tuition_min": 4000, "tuition_max": 7000,
     "website": "https://www.hit.edu.cn", "latitude": 45.7411, "longitude": 126.6278},
    {"name": "中山大学", "province": "广东", "city": "广州", "level": "985", "type": "综合",
     "tags": ["985", "211", "双一流"], "tuition_min": 5160, "tuition_max": 8000,
     "website": "https://www.sysu.edu.cn", "latitude": 23.0934, "longitude": 113.2971},
    {"name": "四川大学", "province": "四川", "city": "成都", "level": "985", "type": "综合",
     "tags": ["985", "211", "双一流"], "tuition_min": 4440, "tuition_max": 7500,
     "website": "https://www.scu.edu.cn", "latitude": 30.6301, "longitude": 104.0826},
    {"name": "北京航空航天大学", "province": "北京", "city": "北京", "level": "985", "type": "理工",
     "tags": ["985", "211", "双一流"], "tuition_min": 5000, "tuition_max": 8000,
     "website": "https://www.buaa.edu.cn", "latitude": 39.9831, "longitude": 116.3474},
    {"name": "同济大学", "province": "上海", "city": "上海", "level": "985", "type": "理工",
     "tags": ["985", "211", "双一流"], "tuition_min": 5500, "tuition_max": 9000,
     "website": "https://www.tongji.edu.cn", "latitude": 31.2837, "longitude": 121.5019},
]


async def seed():
    async with async_session() as session:
        for data in UNIVERSITIES:
            uni = University(id=uuid.uuid4(), **data)
            session.add(uni)
        await session.commit()
        print(f"Inserted {len(UNIVERSITIES)} universities")


if __name__ == "__main__":
    asyncio.run(seed())