from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    #COMMON
    url(r'^features/$', 'bee.views.common.features', name='features'),
    url(r'^pricing/$', 'bee.views.common.pricing', name='pricing'),
    url(r'^help_and_community/$', 'bee.views.common.help_and_community', name='help_and_community'),
    url(r'^about/$', 'bee.views.common.about', name='about'),

    #AUTH
    url(r'^login/$', 'bee.views.auth.login_user', name='login'),
    url(r'^register/$', 'bee.views.auth.register',  name='register'),
    url(r'^activate_email/$', 'bee.views.auth.activate', name='activate_email'),

    #PROJECTS, SPRINTS & TASKS
    url(r'^projects/$', 'bee.views.psttasks.projects', name='projects_list'),
    url(r'^project/(?P<proj_id>\d+)/$', 'bee.views.psttasks.project', name='project'),
    url(r'^create_project/$', 'bee.views.psttasks.create_project', name='create_project'),

    #PROFILE SUMMARY

    #MESSAGING & DISCUSSION

)