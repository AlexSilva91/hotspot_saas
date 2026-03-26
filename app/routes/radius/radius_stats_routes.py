from flask import Blueprint, jsonify, render_template, current_app, request
from flask_login import login_required
from app.services.radius.radius_accounting_service import RadiusAccountingService
from app.services.radius.radius_user_service import RadiusUserService
from app.services.radius.radius_reply_service import RadiusReplyService
from sqlalchemy import text
from datetime import datetime
import logging

radius_stats_bp = Blueprint("radius_stats", __name__)
logger = logging.getLogger(__name__)


@radius_stats_bp.route("/radius/dashboard", methods=["GET"])
@login_required
def dashboard():
    """Página de estatísticas RADIUS"""
    
    # Verificar se RADIUS está ativado
    if not current_app.config.get('USE_RADIUS', False):
        return render_template(
            "radius/disabled.html",
            message="RADIUS não está ativado no sistema. Configure USE_RADIUS=True no .env"
        )
    
    # Busca dados do dashboard
    dashboard_result = RadiusAccountingService.get_tenant_dashboard()
    dashboard_data = dashboard_result.get('data', {}) if dashboard_result.get('success') else {}
    
    # Busca usuários RADIUS
    users_result = RadiusUserService.list()
    users = users_result.get('data', []) if users_result.get('success') else []
    
    # Busca sessões ativas para detalhes
    sessions_result = RadiusAccountingService.get_active_sessions()
    active_sessions = sessions_result.get('data', []) if sessions_result.get('success') else []
    
    return render_template(
        "radius/dashboard.html",
        dashboard=dashboard_data,
        users=users,
        active_sessions=active_sessions[:10],  # Top 10 sessões
        total_sessions=len(active_sessions)
    )


@radius_stats_bp.route("/radius/user/<username>/stats", methods=["GET"])
@login_required
def user_stats(username):
    """Estatísticas detalhadas de um usuário"""
    
    # Verificar se RADIUS está ativado
    if not current_app.config.get('USE_RADIUS', False):
        return render_template("radius/disabled.html")
    
    # Busca resumo do usuário
    summary_result = RadiusAccountingService.get_user_summary(username)
    summary = summary_result.get('data', {}) if summary_result.get('success') else {}
    
    # Busca histórico de sessões
    history_result = RadiusAccountingService.get_user_history(username, limit=100)
    sessions = history_result.get('data', []) if history_result.get('success') else []
    
    # Busca rate limit do usuário
    rate_limit_result = RadiusReplyService.get_user_rate_limit(username)
    rate_limit = rate_limit_result.get('data') if rate_limit_result.get('success') else None
    
    # Busca sessão atual (se estiver online)
    current_session = None
    for session in sessions:
        if session.is_active:
            current_session = session
            break
    
    return render_template(
        "radius/user_stats.html",
        username=username,
        summary=summary,
        sessions=sessions,
        rate_limit=rate_limit,
        current_session=current_session,
        total_sessions=len(sessions)
    )


@radius_stats_bp.route("/api/radius/active-sessions", methods=["GET"])
@login_required
def api_active_sessions():
    """API para sessões ativas (para charts)"""
    
    result = RadiusAccountingService.get_active_sessions()
    if result['success']:
        # Formata para JSON usando os atributos corretos do model
        sessions = []
        for s in result['data']:
            sessions.append({
                'username': s.username,
                'ip': str(s.framedipaddress) if s.framedipaddress else None,
                'mac': s.callingstationid,
                'start_time': s.acctstarttime.isoformat() if s.acctstarttime else None,
                'session_time': s.acctsessiontime or 0,
                'session_time_formatted': format_session_time(s.acctsessiontime or 0),
                'input_mb': round((s.acctinputoctets or 0) / (1024 * 1024), 2),
                'output_mb': round((s.acctoutputoctets or 0) / (1024 * 1024), 2),
                'nas_ip': str(s.nasipaddress) if s.nasipaddress else None
            })
        return jsonify({'success': True, 'data': sessions, 'count': len(sessions)})
    
    return jsonify({'success': False, 'error': result.get('errors')}), 500


@radius_stats_bp.route("/api/radius/traffic/<username>", methods=["GET"])
@login_required
def api_user_traffic(username):
    """API para tráfego de um usuário"""
    
    result = RadiusAccountingService.get_user_summary(username)
    if result['success']:
        data = result['data']
        return jsonify({
            'success': True,
            'data': {
                'username': username,
                'total_time': data.get('total_time', 0),
                'total_time_hours': data.get('total_time_hours', 0),
                'total_input_mb': data.get('total_input_mb', 0),
                'total_output_mb': data.get('total_output_mb', 0),
                'total_traffic_mb': data.get('total_traffic_mb', 0),
                'session_count': data.get('session_count', 0)
            }
        })
    
    return jsonify({'success': False, 'error': result.get('errors')}), 500


@radius_stats_bp.route("/api/radius/user/<username>/sessions", methods=["GET"])
@login_required
def api_user_sessions(username):
    """API para histórico de sessões de um usuário"""
    
    limit = request.args.get('limit', 50, type=int)
    result = RadiusAccountingService.get_user_history(username, limit)
    
    if result['success']:
        sessions = []
        for s in result['data']:
            sessions.append({
                'radacctid': s.radacctid,
                'acctsessionid': s.acctsessionid,
                'start_time': s.acctstarttime.isoformat() if s.acctstarttime else None,
                'stop_time': s.acctstoptime.isoformat() if s.acctstoptime else None,
                'session_time': s.acctsessiontime or 0,
                'input_mb': round((s.acctinputoctets or 0) / (1024 * 1024), 2),
                'output_mb': round((s.acctoutputoctets or 0) / (1024 * 1024), 2),
                'ip': str(s.framedipaddress) if s.framedipaddress else None,
                'mac': s.callingstationid,
                'terminate_cause': s.acctterminatecause,
                'is_active': s.is_active
            })
        return jsonify({'success': True, 'data': sessions, 'count': len(sessions)})
    
    return jsonify({'success': False, 'error': result.get('errors')}), 500


@radius_stats_bp.route("/api/radius/online-count", methods=["GET"])
@login_required
def api_online_count():
    """API para número de usuários online"""
    
    result = RadiusAccountingService.get_active_sessions_count()
    if result['success']:
        return jsonify({'success': True, 'online': result['data']})
    
    return jsonify({'success': False, 'error': result.get('errors')}), 500


@radius_stats_bp.route("/api/radius/today-traffic", methods=["GET"])
@login_required
def api_today_traffic():
    """API para tráfego de hoje"""
    
    result = RadiusAccountingService.get_today_traffic()
    if result['success']:
        return jsonify({'success': True, 'data': result['data']})
    
    return jsonify({'success': False, 'error': result.get('errors')}), 500

@radius_stats_bp.route("/api/radius/status", methods=["GET"])
@login_required
def api_radius_status():
    """API para status do RADIUS"""
    
    try:
        # Testa conexão com o banco
        from app.extensions import db
        db.session.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Verifica se há sessões ativas
    active_count = RadiusAccountingService.get_active_sessions_count()
    
    return jsonify({
        'success': True,
        'data': {
            'enabled': current_app.config.get('USE_RADIUS', False),
            'hybrid_mode': current_app.config.get('HYBRID_MODE', True),
            'database': db_status,
            'active_sessions': active_count.get('data', 0) if active_count.get('success') else 0,
            'timestamp': datetime.now().isoformat()
        }
    })

def format_session_time(seconds):
    """Formata tempo de sessão em formato legível"""
    if not seconds:
        return "0s"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


