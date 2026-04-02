import pytest

from src.exceptions.custom import CustomExc
from src.services.push_service import PushService


class FakeApiClient:
    async def post_selection(self, payload):
        if payload[0] == "bad":
            raise CustomExc("fail")
        return "ok"


class TestPushService:
    @pytest.mark.asyncio
    async def test_push_all_success(self):
        """Проверка успешной отправки всех дисциплин"""
        client = FakeApiClient()
        service = PushService(client)

        selection = {
            "1": ["a"],
            "2": ["b"],
        }

        results = await service.push_all(selection)

        assert len(results) == 2
        assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_push_partial_fail(self):
        """Проверка частичной отправки всех дисциплин"""
        client = FakeApiClient()
        service = PushService(client)

        selection = {
            "ok": ["1"],
            "bad": ["2"],
        }

        results = await service.push_all(selection)

        assert any(r.success for r in results)
        assert any(not r.success for r in results)

    @pytest.mark.asyncio
    async def test_error_mapping(self):
        """Проверка неуспешной отправки всех дисциплин"""
        client = FakeApiClient()
        service = PushService(client)

        results = await service.push_all({"bad": ["1"]})

        assert results[0].error == "fail"

    @pytest.mark.asyncio
    async def test_on_progress_called(self):
        """Проверка on_progress возвращает ли корректно"""
        client = FakeApiClient()

        calls = []

        def spy(result, completed, total):
            calls.append((completed, total))

        service = PushService(client, on_progress=spy)

        selection = {
            "1": ["a"],
            "2": ["b"],
        }

        await service.push_all(selection)

        assert len(calls) == 2
        assert calls[-1] == (2, 2)
