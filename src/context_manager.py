# -*- coding: utf -8 -*- #
"""
@filename:context_manager.py
@author:ChenWenGang
@time:2026-01-20
"""
import uuid
import time
from typing import Dict, Optional


class SessionContext:
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.generated_case_path: str = ""  # 会话内生成的测试用例路径
        self.create_time = time.time()
        self.expire_seconds: int = 60 * 60 * 24  # 未刷新页面或未关闭浏览器重新打开，24小时后session过期
        self.expire_time: float = self.create_time + self.expire_seconds

    # 将类的方法转为属性，使用时不需要加括号
    @property
    def is_expired(self) -> bool:
        """判断当前会话是否过期"""
        return time.time() > self.expire_time


class SessionContextManager:
    """全局上下文管理器"""

    def __init__(self):
        self.sessions: Dict[str, SessionContext] = {}

    def _clean_expired_session(self):
        """清理过期的会话"""
        for session_id, session in self.sessions.items():
            if session.is_expired:
                del self.sessions[session_id]

    def get_session(self, session_id: Optional[str] = None) -> SessionContext:
        """
        获取/创建会话上下文
        :param session_id: 前端传递的会话ID（是str或None类型，默认为None）
        :return 会话上下文实例
        """
        self._clean_expired_session()
        # 无ID/ID不存在时，创建新的会话
        if not session_id or session_id not in self.sessions:
            new_session = SessionContext()
            self.sessions[new_session.session_id] = new_session
            return new_session
        # 有有效ID，返回现有会话（刷新过期时间）
        session = self.sessions[session_id]
        session.expire_time = time.time() + session.expire_seconds
        return session

    def save_case_path(self, session_id: str, case_path: str):
        """保存会话内生成的测试用例路径"""
        session = self.get_session(session_id)
        session.generated_case_path = case_path

    def get_case_path(self, session_id: str) -> str:
        """获取会话内生成的测试用例路径"""
        session = self.get_session(session_id)
        return session.generated_case_path if not session.is_expired else ""

# 全局单例
session_manager=SessionContextManager()


if __name__ == '__main__':
    pass
