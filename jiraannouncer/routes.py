def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('announce', '/announce')
    config.add_route('github', '/github')
    config.add_route('travis', '/travis')
    config.add_route('jira', '/jira')
    config.add_route('circle', '/circle')