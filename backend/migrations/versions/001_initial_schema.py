"""initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-08 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=False, server_default='UTC'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('settings_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Market Candles
    op.create_table(
        'market_candles',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('timeframe', sa.String(length=10), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('open', sa.Float(), nullable=False),
        sa.Column('high', sa.Float(), nullable=False),
        sa.Column('low', sa.Float(), nullable=False),
        sa.Column('close', sa.Float(), nullable=False),
        sa.Column('tick_volume', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('symbol', 'timeframe', 'timestamp', name='uq_candle')
    )
    op.create_index('ix_candle_symbol_tf_ts', 'market_candles', ['symbol', 'timeframe', 'timestamp'])
    op.create_index('ix_candle_timestamp', 'market_candles', ['timestamp'])

    # Market Quotes
    op.create_table(
        'market_quotes',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('bid', sa.Float(), nullable=False),
        sa.Column('ask', sa.Float(), nullable=False),
        sa.Column('spread', sa.Float(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_quote_symbol', 'market_quotes', ['symbol'])

    # Economic Events
    op.create_table(
        'economic_events',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('event', sa.String(length=255), nullable=False),
        sa.Column('importance', sa.String(length=20), nullable=False),
        sa.Column('actual', sa.Float(), nullable=True),
        sa.Column('forecast', sa.Float(), nullable=True),
        sa.Column('previous', sa.Float(), nullable=True),
        sa.Column('event_code', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_econ_event_ts', 'economic_events', ['timestamp'])
    op.create_index('ix_econ_event_currency', 'economic_events', ['currency'])
    op.create_index('ix_econ_event_importance', 'economic_events', ['importance'])

    # Signals
    op.create_table(
        'signals',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('timeframe', sa.String(length=10), nullable=False, server_default='M15'),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('bias', sa.String(length=20), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('regime', sa.String(length=30), nullable=False),
        sa.Column('bull_probability', sa.Float(), nullable=False),
        sa.Column('bear_probability', sa.Float(), nullable=False),
        sa.Column('neutral_probability', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('direction', sa.String(length=10), nullable=True),
        sa.Column('entry_low', sa.Float(), nullable=True),
        sa.Column('entry_high', sa.Float(), nullable=True),
        sa.Column('stop_loss', sa.Float(), nullable=True),
        sa.Column('take_profit', sa.Float(), nullable=True),
        sa.Column('risk_reward', sa.Float(), nullable=True),
        sa.Column('atr14', sa.Float(), nullable=True),
        sa.Column('spread', sa.Float(), nullable=True),
        sa.Column('session_name', sa.String(length=30), nullable=True),
        sa.Column('news_clear', sa.Boolean(), nullable=True),
        sa.Column('liquidity_ok', sa.Boolean(), nullable=True),
        sa.Column('spread_ok', sa.Boolean(), nullable=True),
        sa.Column('model_version', sa.String(length=100), nullable=False),
        sa.Column('explanation_json', sa.Text(), nullable=True),
        sa.Column('outcome', sa.String(length=20), nullable=True),
        sa.Column('outcome_pnl', sa.Float(), nullable=True),
        sa.Column('outcome_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_signal_symbol_ts', 'signals', ['symbol', 'timestamp'])
    op.create_index('ix_signal_status', 'signals', ['status'])

    # Signal Reasons
    op.create_table(
        'signal_reasons',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('signal_id', sa.BigInteger(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('value', sa.String(length=100), nullable=True),
        sa.Column('sentiment', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['signal_id'], ['signals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Model Versions
    op.create_table(
        'model_versions',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('version', sa.String(length=100), nullable=False),
        sa.Column('model_type', sa.String(length=50), nullable=False),
        sa.Column('state', sa.String(length=20), nullable=False, server_default='TRAINING'),
        sa.Column('training_start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('training_end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('validation_start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('validation_end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('test_start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('test_end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('feature_count', sa.Integer(), nullable=True),
        sa.Column('feature_names_json', sa.Text(), nullable=True),
        sa.Column('hyperparameters_json', sa.Text(), nullable=True),
        sa.Column('label_config_json', sa.Text(), nullable=True),
        sa.Column('calibration_method', sa.String(length=50), nullable=True),
        sa.Column('metrics_json', sa.Text(), nullable=True),
        sa.Column('accuracy', sa.Float(), nullable=True),
        sa.Column('balanced_accuracy', sa.Float(), nullable=True),
        sa.Column('brier_score', sa.Float(), nullable=True),
        sa.Column('log_loss', sa.Float(), nullable=True),
        sa.Column('profit_factor', sa.Float(), nullable=True),
        sa.Column('sharpe_ratio', sa.Float(), nullable=True),
        sa.Column('max_drawdown', sa.Float(), nullable=True),
        sa.Column('win_rate', sa.Float(), nullable=True),
        sa.Column('artifacts_path', sa.String(length=500), nullable=True),
        sa.Column('git_commit', sa.String(length=40), nullable=True),
        sa.Column('feature_importance_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('version')
    )

    # Alerts
    op.create_table(
        'alerts',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('alert_type', sa.String(length=50), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False, server_default='GBPUSD'),
        sa.Column('min_confidence', sa.Float(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('config_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_alert_user', 'alerts', ['user_id'])

    # Notifications
    op.create_table(
        'notifications',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('alert_id', sa.BigInteger(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('notification_type', sa.String(length=50), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('data_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['alert_id'], ['alerts.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_notification_user', 'notifications', ['user_id'])
    op.create_index('ix_notification_read', 'notifications', ['is_read'])

    # Backtest Runs
    op.create_table(
        'backtest_runs',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('model_version', sa.String(length=100), nullable=False),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('config_json', sa.Text(), nullable=False),
        sa.Column('total_trades', sa.Integer(), nullable=True),
        sa.Column('win_rate', sa.Float(), nullable=True),
        sa.Column('profit_factor', sa.Float(), nullable=True),
        sa.Column('sharpe_ratio', sa.Float(), nullable=True),
        sa.Column('sortino_ratio', sa.Float(), nullable=True),
        sa.Column('calmar_ratio', sa.Float(), nullable=True),
        sa.Column('max_drawdown', sa.Float(), nullable=True),
        sa.Column('expectancy', sa.Float(), nullable=True),
        sa.Column('avg_win', sa.Float(), nullable=True),
        sa.Column('avg_loss', sa.Float(), nullable=True),
        sa.Column('results_json', sa.Text(), nullable=True),
        sa.Column('equity_curve_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('backtest_runs')
    op.drop_table('notifications')
    op.drop_table('alerts')
    op.drop_table('model_versions')
    op.drop_table('signal_reasons')
    op.drop_table('signals')
    op.drop_table('economic_events')
    op.drop_table('market_quotes')
    op.drop_table('market_candles')
    op.drop_table('users')
