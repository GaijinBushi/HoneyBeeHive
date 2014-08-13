from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from bee.decorators.permissions import check_project_read_js, check_project_read, check_project_write, \
    check_project_write_js, check_project_admin_js, check_project_admin
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response
from bee.models import Project, UserStory, Sprint, AssignedWorkerToProject
from bee.forms.projects_forms import ProjectForm, UserStoryForm, SprintForm, AddParticipantToProjectForm
import pprint
from django.contrib import messages
import json


@login_required
def projects(request):
    pr_owner_list = list(Project.objects.filter(created_by=request.user))
    pr_participant_list = list(request.user.get_projects_participant_list())
    print pr_participant_list, pr_owner_list
    return render_to_response('templates/bee/scrum_projects/projects.html',
        {'projects_owner': pr_owner_list, 'projects_participant':pr_participant_list},
        context_instance=RequestContext(request))


@login_required
# @require_http_methods(['POST, GET'])
def create_project(request):
    if request.method == 'POST':
        #Trying to create a new project
        new_project = Project(created_by=request.user)
        form = ProjectForm(request.POST, instance=new_project)
        if form.is_valid():
            #the project data is valid
            new_project = form.save()
            #todo testear
            AssignedWorkerToProject.objects.create(uworker=request.user, project=new_project, role="owner", permissions=3)
            #TODO messages.success(request, "project created")
            return HttpResponseRedirect(reverse('project', kwargs={'proj_id': new_project.id}))
        #the project data is not valid
    else:
        #requesting the create project page
        form = ProjectForm()
    #messages.success(request, "Project created")

    return render_to_response('templates/bee/scrum_projects/create_project.html',
        {'form': form, 'user': request.user},
        context_instance=RequestContext(request))


@login_required
@check_project_read
def project(request, proj_id):
    pr = Project.objects.get(id=proj_id)
    return render_to_response('templates/bee/scrum_projects/project.html',
        {'project': pr},
        context_instance=RequestContext(request))


@login_required
@check_project_read
def user_stories(request, proj_id):
    pr = Project.objects.get(id=proj_id)
    return render_to_response('templates/bee/scrum_projects/user_stories.html',
        {'project': pr},
        context_instance=RequestContext(request))


@login_required
@require_GET
@check_project_write
def new_user_story(request, proj_id):
    form = UserStoryForm()
    pr = Project.objects.get(id=proj_id)
    return render_to_response('templates/bee/scrum_projects/new_user_story.html',
        {'project': pr, 'user_story_form': form},
        context_instance=RequestContext(request))


@login_required
@require_POST
@check_project_write
def create_user_story(request, proj_id):
    pr = Project.objects.get(id=proj_id)
    user_story = UserStory(owner=request.user, project=pr)
    form = UserStoryForm(request.POST, instance=user_story)
    if form.is_valid():
        user_story = form.save()
        #TODO messages.success(request, "user-story created")
        return HttpResponseRedirect(reverse('user_stories', kwargs={'proj_id': pr.id}))
    else:
        return render_to_response('templates/bee/scrum_projects/new_user_story.html',
        {'project': pr, 'user_story_form': form},
        context_instance=RequestContext(request))


@login_required
@check_project_admin
def gantt_diagram(request, proj_id):
    pr = Project.objects.get(id=proj_id)
    return render_to_response('templates/bee/scrum_projects/gantt_diagram.html',
        {'project': pr},
        context_instance=RequestContext(request))


@login_required
@check_project_read
def sprints(request, proj_id):
    pr = Project.objects.get(id=proj_id)
    project_sprints = pr.sprints.order_by('id')
    return render_to_response('templates/bee/scrum_projects/sprints.html',
        {'project': pr, 'sprints': project_sprints},
        context_instance=RequestContext(request))


@login_required
@check_project_admin
def create_sprint_colorbox(request, proj_id):
    form = SprintForm()
    pr = Project.objects.get(id=proj_id)
    return render_to_response('templates/bee/scrum_projects/_sprint_creation_form.html',
        {'project': pr, 'sprint_form': form},
        context_instance=RequestContext(request))


@login_required
@check_project_admin_js
def create_sprint_js(request, proj_id):
    pr = Project.objects.get(id=proj_id)
    reset_dom = 'true' if pr.sprints.count() == 0 else 'false'
    spr = Sprint(project=pr)
    form = SprintForm(request.POST, instance=spr)
    #todo revisar permisos
    if form.is_valid():
        spr = form.save()
        return render_to_response('templates/bee/scrum_projects/_create_sprint.js',
            {'project': pr, 'sprint': spr, 'reset_dom':reset_dom}, content_type='text/x-javascript',
            context_instance=RequestContext(request))
    else:
        return render_to_response('templates/bee/scrum_projects/_create_sprint_error.js',
                {'project': pr, 'sprint': spr}, content_type='text/x-javascript',
                context_instance=RequestContext(request))


@login_required
@check_project_admin
def niko_calendar(request, proj_id):
    pr = Project.objects.get(id=proj_id)
    return render_to_response('templates/bee/scrum_projects/niko_calendar.html',
        {'project': pr},
        context_instance=RequestContext(request))


@login_required
@check_project_admin
def admin_project(request, proj_id):
    pr = Project.objects.get(id=proj_id)
    form = AddParticipantToProjectForm()
    return render_to_response('templates/bee/scrum_projects/admin_project.html',
        {'project': pr, 'add_participant_form': form},
        context_instance=RequestContext(request))


@login_required
@check_project_admin_js
def add_participant_to_project(request, proj_id): #todo mostrar error al fallar
    pr = Project.objects.get(id=proj_id)
    awtp = AssignedWorkerToProject(project=pr)
    form = AddParticipantToProjectForm(request.POST, instance=awtp)
    if form.is_valid():
        awtp = form.save()
        return render_to_response('templates/bee/scrum_projects/_add_participant_to_project.js',
                {'project': pr, 'awtp': awtp}, content_type='text/x-javascript',
                context_instance=RequestContext(request))

    return render_to_response('templates/bee/scrum_projects/_add_participant_to_project_error.js',
            {'project': pr, 'awtp': awtp}, content_type='text/x-javascript',
            context_instance=RequestContext(request))