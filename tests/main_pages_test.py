import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_main(async_client: AsyncClient) -> None:
    response = await async_client.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_faq(async_client: AsyncClient) -> None:
    response = await async_client.get("/faq")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_pay_return(async_client: AsyncClient) -> None:
    response = await async_client.get("/pay_return")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_tariffs(async_client: AsyncClient) -> None:
    response = await async_client.get("/tariffs")
    assert response.status_code == 200
