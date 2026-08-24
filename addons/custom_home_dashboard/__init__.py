def post_init_hook(env):
    """Make the custom dashboard the default landing page for every user."""
    action = env.ref('custom_home_dashboard.action_custom_home_dashboard', raise_if_not_found=False)
    if not action:
        return
    env['ir.default'].set('res.users', 'action_id', action.id)
    env.user.action_id = action.id
