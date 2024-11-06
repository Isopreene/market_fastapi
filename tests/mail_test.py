from httpx import AsyncClient


async def test_client(async_client: AsyncClient,
                      generate_mail_link,
                      register_user):
    response = await async_client.get('/activate_link')
    assert response.status_code == 404

    link = generate_mail_link()
    response = await async_client.get(link)
    assert response.status_code == 404

    register_user()
    link = generate_mail_link()
    response = await async_client.get(link)
    assert response.status_code == 200
