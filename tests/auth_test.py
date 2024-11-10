import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_register(async_client: AsyncClient) -> None:
    response = await async_client.get("/register")
    assert response.status_code == 2


@pytest.mark.asyncio
async def test_post_right_register(async_client: AsyncClient,
                                   user_right_register_data,
                                   user_wrong_register_data) -> None:
    response = await async_client.post("/register",
                                       json=user_right_register_data)
    assert response.status_code == 200
    response = await async_client.post("/register",
                                       json=user_right_register_data)
    assert response.status_code == 400
    response = await async_client.post("/register",
                                       json=user_wrong_register_data)
    print(response.status_code)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_login(async_client: AsyncClient) -> None:
    response = await async_client.get("/login")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_post_login(async_client: AsyncClient,
                          user_right_register_data,
                          user_right_login_data,
                          user_wrong_login_data) -> None:

    response = await async_client.post("/login",
                                       json=user_right_login_data)
    assert response.status_code == 401

    response = await async_client.post("/login",
                                       json=user_wrong_login_data)
    print(response.status_code)
    assert response.status_code == 404

    response = await async_client.post("/register",
                                       json=user_right_register_data)
    response = await async_client.post("/login",
                                       json=user_right_login_data)
    assert response.status_code == 302

    assert response.headers["Location"] == "/"
    assert response.cookies["access_token"]
    assert response.cookies["token_type"] == "bearer"
    assert response.cookies["login"] == "True"
    assert response.cookies["name"]


@pytest.mark.asyncio
async def test_get_recover(async_client: AsyncClient) -> None:
    response = await async_client.get("/recover")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_post_recover(async_client: AsyncClient,
                            user_right_register_data,
                            user_right_recovery_data,
                            user_wrong_recovery_data) -> None:

    response = await async_client.post("/recover", json=jsonable_encoder(
                                       user_right_recovery_data))
    # переписать данные юзеров под модели, иначе возникает 422
    assert response.status_code == 401

    response = await async_client.post("/recover",
                                       json=user_wrong_recovery_data)
    print(response.status_code)
    assert response.status_code == 404

    response = await async_client.post("/register",
                                       json=user_right_register_data)
    response = await async_client.post("/recover",
                                       json=user_wrong_recovery_data)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_logout(async_client: AsyncClient,):
    response = await async_client.get("/logout")
    assert response.status_code == 302
    assert not response.cookies.get("access_token")
    assert not response.cookies.get("bearer")
    assert not response.cookies.get("login")
    assert not response.cookies.get("name")
