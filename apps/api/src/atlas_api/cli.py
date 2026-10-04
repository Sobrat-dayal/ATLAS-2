import argparse
import asyncio

from atlas.authorization.repository import AuthorizationRepository
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from atlas_api.config import get_settings


async def grant_role(user_id: str, role_key: str):
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async with session_maker() as session:
        repo = AuthorizationRepository(session)
        granted = await repo.grant_role(user_id, role_key, assigned_by_user_id=None)
        await session.commit()

        if granted:
            print(f"Granted role '{role_key}' to user {user_id}")
        else:
            print(f"User {user_id} already has role '{role_key}' or role does not exist")


async def revoke_role(user_id: str, role_key: str):
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async with session_maker() as session:
        repo = AuthorizationRepository(session)
        revoked = await repo.revoke_role(user_id, role_key)
        await session.commit()

        if revoked:
            print(f"Revoked role '{role_key}' from user {user_id}")
        else:
            print(f"User {user_id} did not have role '{role_key}' or role does not exist")


async def list_user_roles(user_id: str):
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async with session_maker() as session:
        repo = AuthorizationRepository(session)
        roles = await repo.get_explicit_user_roles(user_id)

        if roles:
            print(f"Explicit roles for user {user_id}:")
            for role in roles:
                print(f" - {role.key}")
        else:
            print(f"User {user_id} has no explicit roles assigned.")


def main():
    parser = argparse.ArgumentParser(description="ATLAS Authorization Management")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # grant-role
    parser_grant = subparsers.add_parser("grant-role", help="Grant a role to a user")
    parser_grant.add_argument("--user-id", required=True, help="Target Supabase user UUID")
    parser_grant.add_argument("--role", required=True, help="Role key (e.g. admin)")

    # revoke-role
    parser_revoke = subparsers.add_parser("revoke-role", help="Revoke a role from a user")
    parser_revoke.add_argument("--user-id", required=True, help="Target Supabase user UUID")
    parser_revoke.add_argument("--role", required=True, help="Role key (e.g. admin)")

    # list-user-roles
    parser_list = subparsers.add_parser("list-user-roles", help="List roles for a user")
    parser_list.add_argument("--user-id", required=True, help="Target Supabase user UUID")

    args = parser.parse_args()

    if args.command == "grant-role":
        asyncio.run(grant_role(args.user_id, args.role))
    elif args.command == "revoke-role":
        asyncio.run(revoke_role(args.user_id, args.role))
    elif args.command == "list-user-roles":
        asyncio.run(list_user_roles(args.user_id))


if __name__ == "__main__":
    main()
