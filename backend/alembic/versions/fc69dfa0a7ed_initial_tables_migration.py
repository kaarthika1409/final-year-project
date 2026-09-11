"""Initial tables migration

Revision ID: fc69dfa0a7ed
Revises: 
Create Date: 2026-08-13 19:45:27.664758

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fc69dfa0a7ed'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('age', sa.Integer(), nullable=False),
        sa.Column('weight', sa.Float(), nullable=False),
        sa.Column('height', sa.Float(), nullable=False),
        sa.Column('gender', sa.String(), nullable=False),
        sa.Column('activity_level', sa.String(), nullable=False),
        sa.Column('goal', sa.String(), nullable=False),
        sa.Column('dietary_preferences', sa.String(), nullable=True, server_default='balanced'),
        sa.Column('allergies', sa.String(), nullable=True, server_default=''),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    op.create_table(
        'meal_slots',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('default_weight_pct', sa.Float(), nullable=False),
    )
    op.create_index(op.f('ix_meal_slots_id'), 'meal_slots', ['id'], unique=False)

    op.create_table(
        'nutrition_reference',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('food_name', sa.String(), nullable=False),
        sa.Column('calories', sa.Float(), nullable=False),
        sa.Column('protein', sa.Float(), nullable=False),
        sa.Column('carbs', sa.Float(), nullable=False),
        sa.Column('fat', sa.Float(), nullable=False),
        sa.Column('serving_size_g', sa.Float(), nullable=True, server_default='100.0'),
        sa.Column('category', sa.String(), nullable=True, server_default='general'),
        sa.Column('allergens', sa.String(), nullable=True, server_default=''),
        sa.Column('tags', sa.String(), nullable=True, server_default=''),
    )
    op.create_index(op.f('ix_nutrition_reference_id'), 'nutrition_reference', ['id'], unique=False)
    op.create_index(op.f('ix_nutrition_reference_food_name'), 'nutrition_reference', ['food_name'], unique=True)

    op.create_table(
        'meal_logs',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('meal_slot_id', sa.Integer(), sa.ForeignKey('meal_slots.id'), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('meal_slot', sa.String(), nullable=False),
        sa.Column('food_name', sa.String(), nullable=False),
        sa.Column('quantity_g', sa.Float(), nullable=False, server_default='100.0'),
        sa.Column('calories', sa.Float(), nullable=False),
        sa.Column('protein_g', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('carbs_g', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('fat_g', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('source', sa.String(), nullable=False, server_default='manual'),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=True),
    )
    op.create_index(op.f('ix_meal_logs_id'), 'meal_logs', ['id'], unique=False)

    op.create_table(
        'daily_targets',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('date', sa.String(), nullable=False),
        sa.Column('bmr', sa.Float(), nullable=False),
        sa.Column('target_calories', sa.Float(), nullable=False),
        sa.Column('consumed_calories', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('remaining_calories', sa.Float(), nullable=False),
        sa.Column('slot_targets', sa.JSON(), nullable=True),
        sa.Column('target_protein', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('target_carbs', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('target_fat', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('consumed_protein', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('consumed_carbs', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('consumed_fat', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('breakfast_target', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('lunch_target', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('snacks_target', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('dinner_target', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('breakfast_consumed', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('lunch_consumed', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('snacks_consumed', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('dinner_consumed', sa.Float(), nullable=True, server_default='0.0'),
    )
    op.create_index(op.f('ix_daily_targets_id'), 'daily_targets', ['id'], unique=False)
    op.create_index(op.f('ix_daily_targets_date'), 'daily_targets', ['date'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('daily_targets')
    op.drop_table('meal_logs')
    op.drop_table('nutrition_reference')
    op.drop_table('meal_slots')
    op.drop_table('users')
