#!/bin/bash
set -e

echo "🌱 Seeding Initial Data"
echo "========================"

# Check if backend container is running
if ! docker-compose ps backend | grep -q "Up"; then
    echo "❌ Backend container is not running. Please start it first:"
    echo "   docker-compose up -d backend"
    exit 1
fi

# Check if migrations have been run
echo "⏳ Checking if migrations have been run..."
MIGRATION_STATUS=$(docker-compose exec -T backend alembic current 2>&1)
if [ $? -ne 0 ]; then
    echo "❌ Migrations have not been run. Please run migrations first:"
    echo "   ./scripts/run-migrations.sh"
    exit 1
fi

echo "✅ Migrations are up to date"

# Seed data using Python script
echo "⏳ Seeding initial data..."
docker-compose exec -T backend python -c "
from app.db.session import SessionLocal
from app.models.user import Role, Permission
from app.models.base import Base

db = SessionLocal()
try:
    # Check if roles already exist
    existing_roles = db.query(Role).count()
    if existing_roles > 0:
        print('✅ Roles already exist. Skipping seed.')
    else:
        # Create default roles
        roles = [
            Role(name='owner', description='System owner with full privileges', is_system_role=True),
            Role(name='admin', description='Administrator with management access', is_system_role=True),
            Role(name='staff', description='Staff member with limited access', is_system_role=True),
            Role(name='customer', description='End customer', is_system_role=True),
        ]
        db.add_all(roles)
        db.commit()
        print('✅ Default roles created successfully!')
        
        # Create default permissions
        permissions = [
            Permission(name='user.create', description='Create new user accounts', resource='users', action='create'),
            Permission(name='user.read', description='View user information', resource='users', action='read'),
            Permission(name='user.update', description='Update user information', resource='users', action='update'),
            Permission(name='user.delete', description='Delete user accounts', resource='users', action='delete'),
            Permission(name='trading.place_order', description='Place trading orders', resource='trading', action='create'),
            Permission(name='trading.view_positions', description='View trading positions', resource='trading', action='read'),
            Permission(name='financial.deposit', description='Process deposits', resource='financial', action='create'),
            Permission(name='financial.withdraw', description='Process withdrawals', resource='financial', action='create'),
            Permission(name='admin.dashboard', description='Access admin dashboard', resource='admin', action='read'),
            Permission(name='compliance.view_reports', description='View compliance reports', resource='compliance', action='read'),
        ]
        db.add_all(permissions)
        db.commit()
        print('✅ Default permissions created successfully!')
        
except Exception as e:
    print(f'❌ Error seeding data: {e}')
    db.rollback()
    raise
finally:
    db.close()
"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Data seeding completed successfully!"
else
    echo "❌ Data seeding failed!"
    exit 1
fi

