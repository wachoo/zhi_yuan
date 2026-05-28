"""种子数据：常见本科专业"""
import asyncio
import uuid
import sys
sys.path.insert(0, "backend")

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session
from app.models.major import Major

MAJORS = [
    {"name": "计算机科学与技术", "category": "工学", "duration": 4,
     "courses": ["数据结构", "操作系统", "计算机网络", "数据库", "编译原理", "算法设计"],
     "career_directions": ["软件工程师", "算法工程师", "系统架构师", "数据工程师"],
     "avg_salary": 15000,
     "subject_requirements": {"must": ["物理"], "prefer": ["化学"]}},
    {"name": "软件工程", "category": "工学", "duration": 4,
     "courses": ["程序设计", "数据结构", "软件工程导论", "软件测试", "项目管理"],
     "career_directions": ["软件开发", "项目经理", "产品经理", "测试工程师"],
     "avg_salary": 14000,
     "subject_requirements": {"must": ["物理"]}},
    {"name": "电子信息工程", "category": "工学", "duration": 4,
     "courses": ["电路分析", "信号与系统", "数字电路", "模拟电路", "通信原理"],
     "career_directions": ["硬件工程师", "通信工程师", "嵌入式开发", "IC设计"],
     "avg_salary": 12000,
     "subject_requirements": {"must": ["物理"]}},
    {"name": "临床医学", "category": "医学", "duration": 5,
     "courses": ["人体解剖学", "生理学", "病理学", "药理学", "内科学", "外科学"],
     "career_directions": ["临床医生", "医学研究", "公共卫生"],
     "avg_salary": 10000,
     "subject_requirements": {"must": ["物理", "化学"]}},
    {"name": "金融学", "category": "经济学", "duration": 4,
     "courses": ["微观经济学", "宏观经济学", "金融学", "投资学", "金融工程"],
     "career_directions": ["银行", "证券", "基金", "保险", "金融科技"],
     "avg_salary": 12000,
     "subject_requirements": {}},
    {"name": "法学", "category": "法学", "duration": 4,
     "courses": ["宪法", "民法", "刑法", "行政法", "国际法", "诉讼法"],
     "career_directions": ["律师", "法官", "检察官", "法务", "公务员"],
     "avg_salary": 10000,
     "subject_requirements": {}},
    {"name": "英语", "category": "文学", "duration": 4,
     "courses": ["综合英语", "英语写作", "翻译理论与实践", "英美文学", "语言学"],
     "career_directions": ["翻译", "外贸", "教育", "国际组织"],
     "avg_salary": 8000,
     "subject_requirements": {}},
    {"name": "土木工程", "category": "工学", "duration": 4,
     "courses": ["结构力学", "材料力学", "土力学", "混凝土结构", "钢结构"],
     "career_directions": ["结构设计", "施工管理", "工程造价", "监理"],
     "avg_salary": 9000,
     "subject_requirements": {"must": ["物理"]}},
    {"name": "会计学", "category": "管理学", "duration": 4,
     "courses": ["基础会计", "中级财务会计", "审计学", "成本管理", "税法"],
     "career_directions": ["会计师", "审计师", "财务分析", "税务师"],
     "avg_salary": 9000,
     "subject_requirements": {}},
    {"name": "人工智能", "category": "工学", "duration": 4,
     "courses": ["机器学习", "深度学习", "自然语言处理", "计算机视觉", "强化学习"],
     "career_directions": ["AI工程师", "算法研究员", "数据科学家"],
     "avg_salary": 18000,
     "subject_requirements": {"must": ["物理"]}},
]


async def seed():
    async with async_session() as session:
        for data in MAJORS:
            major = Major(id=uuid.uuid4(), **data)
            session.add(major)
        await session.commit()
        print(f"Inserted {len(MAJORS)} majors")


if __name__ == "__main__":
    asyncio.run(seed())