from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.forms import formset_factory

from .models import Community, Member, Ministry, CommunityLeader
from users.models import UserProfile
from .forms import MemberForm, MinistryForm, ShepherdForm
from django.contrib import messages

@login_required
def table_members(request):
    template = "members/table.html"
    members = Member.objects.active()
    profile = UserProfile.objects.get_or_create(user=request.user)
    context = {"members": members, "members_active_list": "active", "profile": profile}
    return render(request, template, context)


@login_required
def thumbnail_members(request):
    template = "members/thumbnail.html"
    members = Member.objects.active()
    shepherds = CommunityLeader.objects.all()
    ministries = Ministry.objects.all()
    profile = UserProfile.objects.get_or_create(user=request.user)
    context = {"members": members, "members_active_list": "active", "ministries": ministries, "shepherds": shepherds, "profile": profile}
    return render(request, template, context)


@login_required
def list_members(request):
    template = "members/list.html"
    members = Member.objects.active()
    shepherds = CommunityLeader.objects.all()
    ministries = Ministry.objects.all()
    profile = UserProfile.objects.get_or_create(user=request.user)
    context = {
        "profile": profile,
        "members": members, "shepherds": shepherds, "ministries": ministries, "total": len(members),
        "total_tithe": len(Member.objects.pays_tithe()),
        "total_new_believers": len(Member.objects.new_believer_school()),
        "total_schooling": len(Member.objects.schooling()),
        "total_working": len(Member.objects.working()),
        "total_delete": len(members),
        "status": "all"
    }
    return render(request, template, context)


@login_required
def list_deleted_members(request):
    template = "members/list.html"
    members = Member.objects.deleted()
    shepherds = Community.objects.all()
    ministries = Ministry.objects.all()
    profile = UserProfile.objects.get_or_create(user=request.user)
    context = {
        "profile": profile,
        "members": members, "shepherds": shepherds, "ministries": ministries, "total": len(members),
        "total_tithe": len(Member.objects.pays_tithe()),
        "total_new_believers": len(Member.objects.new_believer_school()),
        "total_schooling": len(Member.objects.schooling()),
        "total_working": len(Member.objects.working()),
        "total_delete": len(members),
        "status": "all",
        "active": "active"
    }
    return render(request, template, context)


@login_required
def detail_member(request, pk):
    template = "members/detail.html"
    member = get_object_or_404(Member, pk=pk)
    profile = UserProfile.objects.get_or_create(user=request.user)
    context = {"member": member, "profile": profile}
    return render(request, template, context)


@login_required
def edit_member(request, pk):
    template = "members/edit.html"
    member = get_object_or_404(Member, pk=pk)
    form = MemberForm()
    shepherds = CommunityLeader.objects.all()
    ministries = Ministry.objects.all()
    profile = UserProfile.objects.get_or_create(user=request.user)
    picture = Member.objects.get(pk=pk).picture
    context = {"member": member, "form": form, "shepherds": shepherds, "ministries": ministries, "profile": profile,"picture": picture}
    return render(request, template, context)


@login_required
def update_member(request, pk):
    if request.method == "POST":
        member = get_object_or_404(Member, pk=pk)
        form = MemberForm(request.POST, request.FILES, instance=member)
        # import pdb; pdb.set_trace()
        if form.is_valid():
            form.save()
            messages.success(request, "Member Information Updated Successfully")
            return redirect("detail_member", pk=pk)
        else:
            messages.error(request, "Member Information Not Updated")
            return redirect("edit_member", pk=pk)


@login_required
def delete_member(request, pk):
    # TODO: Make this functionality available only to admins
    member = get_object_or_404(Member, pk=pk)
    member.active = False
    member.save()
    messages.success(request, "Member Deleted Successfully")
    return redirect("list_members")


@login_required
def restore_member(request, pk):
    # TODO: Make this functionality available only to admins
    member = get_object_or_404(Member, pk=pk)
    member.active = True
    member.save()
    messages.success(request, "Member Restored Successfully")
    return redirect("list_members")


@login_required
def search_members(request):
    template = "members/list.html"
    q = request.GET.get('q')
    shepherds = CommunityLeader.objects.all()
    ministries = Ministry.objects.all()
    profile = UserProfile.objects.get_or_create(user=request.user)
    context = {"ministries": ministries, "shepherds": shepherds, "profile": profile}
    if q != '':
        qs = Member.objects.active().filter(
            Q(name__icontains=q) | Q(shepherd__name__icontains=q) | Q(ministry__name__icontains=q)|
            Q(location__icontains=q) | Q(fathers_name__contains=q) | Q(mothers_name__contains=q)
        )
        context["members"] = qs
        context['total'] = len(qs)
        return render(request, template, context)
    else:
        members = Member.objects.active()
        context['members'] = members
        context['total'] = len(members)
        return render(request, template, context)


@login_required
def get_members_by_statuses(request, status):
    template = "members/list.html"
    shepherds = CommunityLeader.objects.all()
    ministries = Ministry.objects.all()
    profile = UserProfile.objects.get_or_create(user=request.user)
    members = None
    if status == "tithe":
        members = Member.objects.pays_tithe()
    elif status == "new_believers":
        members = Member.objects.new_believer_school()
    elif status == "working":
        members = Member.objects.working()
    elif status == "schooling":
        members = Member.objects.schooling()

    context = {
        "profile": profile,
        "members": members,
        "shepherds": shepherds,
        "ministries": ministries,
        "total": len(Member.objects.active()),
        "total_tithe": len(Member.objects.pays_tithe()),
        "total_new_believers": len(Member.objects.new_believer_school()),
        "total_schooling": len(Member.objects.schooling()),
        "total_working": len(Member.objects.working()),
        "total_delete": len(Member.objects.deleted()),
        status: status,
    }
    return render(request, template, context)


@login_required
def get_members_by_shepherds(request, shepherd):
    template = "members/list.html"
    shepherds = CommunityLeader.objects.all()
    ministries = Ministry.objects.all()
    members = Member.objects.active().filter(shepherd__name__icontains=shepherd)
    profile = UserProfile.objects.get_or_create(user=request.user)
    context = {
        "profile": profile,
        "members": members,
        "shepherds": shepherds,
        "ministries": ministries,
        "total": len(Member.objects.active()),
        "total_tithe": len(Member.objects.pays_tithe()),
        "total_new_believers": len(Member.objects.new_believer_school()),
        "total_schooling": len(Member.objects.schooling()),
        "total_working": len(Member.objects.working()),
        "total_delete": len(Member.objects.deleted()),
        "shepherd_name": shepherd
    }

    return render(request, template, context)


@login_required
def filter_members(request):
    template = "members/thumbnail.html"
    shepherds = CommunityLeader.objects.all()
    ministries = Ministry.objects.all()
    initial_members = Member.objects.active()
    statuses = []
    for i in request.GET:
        if request.GET.get(i) == 'on':
            statuses.append(i)
    for i in statuses:
        if i == 'pays_tithe':
            initial_members = initial_members.filter(pays_tithe=True)
        elif i == 'working':
            initial_members = initial_members.filter(working=True)
        elif i == 'schooling':
            initial_members = initial_members.filter(schooling=True)
        elif i == "new_believer_school":
            initial_members = initial_members.filter(new_believer_school=True)
    # import pdb; pdb.set_trace()

    ministry = request.GET.get('ministry')
    profile = UserProfile.objects.get_or_create(user=request.user)

    context = {
        "profile": profile,
        "members": initial_members,
        "shepherds": shepherds,
        "ministries": ministries,
        "total": len(Member.objects.active()),
        "total_tithe": len(Member.objects.pays_tithe()),
        "total_new_believers": len(Member.objects.new_believer_school()),
        "total_schooling": len(Member.objects.schooling()),
        "total_working": len(Member.objects.working()),
        ministry: ministry
    }
    if ministry is not None:
        initial_members = initial_members.filter(ministry__name__icontains=ministry)
        context['members'] = initial_members
        context['id_ministry'] = ministry

    shepherd = request.GET.get('shepherd')
    if shepherd is not None:
        initial_members = initial_members.filter(shepherd__name__icontains=shepherd)
        # import pdb; pdb.set_trace()
        context['members'] = initial_members

    for i in statuses:
        context[i] = 'checked'

    return render(request, template, context)


from django.views.generic import CreateView, ListView, TemplateView
from django.urls import reverse_lazy

class BaseMemberView:
    template_name = 'members/add.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add mode to context to differentiate between single and multiple
        context['mode'] = getattr(self, 'mode', 'single')
        return context

# Single member creation view
class AddMemberView(BaseMemberView, CreateView):
    model = Member
    form_class = MemberForm
    success_url = reverse_lazy('list_members')
    mode = 'single'
    
    def form_valid(self,form):
        messages.success(self.request, 'Member added successfully!')
        profile = UserProfile.objects.get_or_create(user=self.request.user)
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

# Multiple members creation view
class CreateMembersView(BaseMemberView, TemplateView):
    mode = 'multiple'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add 3 empty forms for multiple member creation
        context['form1'] = MemberForm(prefix='form1')
        context['form2'] = MemberForm(prefix='form2')
        context['form3'] = MemberForm(prefix='form3')
        return context
    
    def post(self, request, *args, **kwargs):
        form1 = MemberForm(request.POST, request.FILES, prefix='form1')
        form2 = MemberForm(request.POST, request.FILES, prefix='form2')
        form3 = MemberForm(request.POST, request.FILES, prefix='form3')
        
        forms = [form1, form2, form3]
        saved_count = 0
        
        for form in forms:
            # Only save forms that have name field filled (at least some data)
            if form.is_valid() and form.cleaned_data.get('name'):
                form.save()
                saved_count += 1
        
        if saved_count > 0:
            messages.success(request, f'Successfully added {saved_count} member(s)!')
            return redirect('member_list')
        else:
            messages.error(request, 'Please fill at least one member form completely.')
            return self.render_to_response({
                'form1': form1,
                'form2': form2,
                'form3': form3,
                'mode': 'multiple'
            })

class MemberListView(ListView):
    model = Member
    template_name = 'members/member_list.html'
    context_object_name = 'members'
    paginate_by = 20

@login_required
def list_ministries(request):
    template = "ministries/list.html"
    ministries = Ministry.objects.all()
    profile = UserProfile.objects.get_or_create(user=request.user)
    context = {"ministries": ministries, "ministries_active_list": "active", "profile": profile}
    return render(request, template, context)


@login_required
def add_ministries(request):
    # TODO: Make this functionality available only to admins
    template = "ministries/add.html"
    form = MinistryForm()
    profile = UserProfile.objects.get_or_create(user=request.user)
    context = {"form": form, "ministries_active_add": "active", "profile": profile}
    return render(request, template, context)


@login_required
def create_ministry(request):
    # TODO: Make this functionality available only to admins
    if request.method == "POST":
        form = MinistryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Ministry Created Successfully")
            return redirect('list_ministries')
        else:
            messages.error(request, "Ministry Creation Failed")
            return redirect('add_ministry')


@login_required
def list_shepherds(request):
    template = "shepherds/list.html"
    profile = UserProfile.objects.get_or_create(user=request.user)
    
    # Get all communities with their leaders
    communities = Community.objects.prefetch_related('leaders').all()
    
    context = {
        "communities": communities,
        "shepherds_active_list": "active", 
        "profile": profile
    }
    return render(request, template, context)

@login_required
def add_shepherd(request):
    template = "shepherds/add.html"
    profile = UserProfile.objects.get_or_create(user=request.user)
    
    # Get existing communities for dropdown
    communities = Community.objects.all()
    
    context = {
        "communities": communities,
        "shepherds_active_add": "active", 
        "profile": profile
    }
    return render(request, template, context)

@login_required
def create_shepherd(request):
    if request.method == "POST":
        community_name = request.POST.get('community_name')
        leader_names = request.POST.getlist('leaders_name[]')
        leader_positions = request.POST.getlist('leaders_position[]')
        leader_descriptions = request.POST.getlist('leaders_description[]')
        leader_phones = request.POST.getlist('leaders_phone[]')
        
        print(f"DEBUG: Processing {len(leader_names)} leaders for community: {community_name}")
        
        # Validate required fields
        if not community_name:
            messages.error(request, "Community name is required")
            return redirect('add_shepherd')
        
        if not leader_names or not any(leader_names):
            messages.error(request, "Please add at least one leader")
            return redirect('add_shepherd')
        
        success_count = 0
        error_messages = []
        
        try:
            # Get or create the Community object
            community, created = Community.objects.get_or_create(name=community_name)
            if created:
                print(f"DEBUG: Created new community: {community_name}")
            else:
                print(f"DEBUG: Using existing community: {community_name}")
        except Exception as e:
            messages.error(request, f"Error with community: {str(e)}")
            return redirect('add_shepherd')
        
        # Process each leader
        for i in range(len(leader_names)):
            # Skip empty entries
            if not leader_names[i] or not leader_positions[i]:
                continue
            
            # Check if position already exists in this community
            existing_leader = CommunityLeader.objects.filter(
                community_name=community,  # Use the Community object, not string
                leader=leader_positions[i]
            ).first()
            
            if existing_leader:
                error_messages.append(
                    f"Position '{leader_positions[i]}' is already assigned to {existing_leader.name} in {community_name}"
                )
                continue
            
            try:
                # Create the leader with Community object
                leader = CommunityLeader(
                    community_name=community,  # Pass the Community object
                    name=leader_names[i],
                    leader=leader_positions[i],
                    description=leader_descriptions[i] if i < len(leader_descriptions) else '',
                    phone=leader_phones[i] if i < len(leader_phones) else ''
                )
                
                leader.save()
                success_count += 1
                print(f"DEBUG: Created leader {leader_names[i]} as {leader_positions[i]}")
                
            except Exception as e:
                error_msg = f"Error creating {leader_names[i]}: {str(e)}"
                error_messages.append(error_msg)
                print(f"DEBUG: Exception: {str(e)}")
        
        # Display results
        if success_count > 0:
            messages.success(request, f"Successfully added {success_count} leader(s) to {community_name}")
        
        for error in error_messages:
            messages.error(request, error)
        
        if success_count == 0 and error_messages:
            return redirect('add_shepherd')
        else:
            return redirect('list_shepherds')
    
    return redirect('add_shepherd')


@login_required
def edit_community(request, community_id):
    template = "shepherds/edit_community.html"
    profile = UserProfile.objects.get_or_create(user=request.user)
    
    try:
        community = Community.objects.get(id=community_id)
        leaders = community.leaders.all()
    except Community.DoesNotExist:
        messages.error(request, "Community not found")
        return redirect('list_shepherds')
    
    if request.method == "POST":
        community_name = request.POST.get('community_name')
        
        if not community_name:
            messages.error(request, "Community name is required")
            return redirect('edit_community', community_id=community_id)
        
        # Update community name
        community.name = community_name
        community.save()
        
        # Update leaders if provided
        leader_ids = request.POST.getlist('leader_ids[]')
        leader_names = request.POST.getlist('leader_names[]')
        leader_positions = request.POST.getlist('leader_positions[]')
        leader_descriptions = request.POST.getlist('leader_descriptions[]')
        leader_phones = request.POST.getlist('leader_phones[]')
        
        # Update existing leaders
        for i, leader_id in enumerate(leader_ids):
            try:
                leader = CommunityLeader.objects.get(id=leader_id, community_name=community)
                if i < len(leader_names):
                    leader.name = leader_names[i]
                if i < len(leader_positions):
                    leader.leader = leader_positions[i]
                if i < len(leader_descriptions):
                    leader.description = leader_descriptions[i]
                if i < len(leader_phones):
                    leader.phone = leader_phones[i]
                leader.save()
            except CommunityLeader.DoesNotExist:
                continue
        
        messages.success(request, f"Community '{community_name}' updated successfully")
        return redirect('list_shepherds')
    
    context = {
        "community": community,
        "leaders": leaders,
        "shepherds_active_list": "active", 
        "profile": profile
    }
    return render(request, template, context)

@login_required
def delete_community(request, community_id):
    if request.method == "POST":
        try:
            community = Community.objects.get(id=community_id)
            community_name = community.name
            community.delete()
            messages.success(request, f"Community '{community_name}' deleted successfully")
        except Community.DoesNotExist:
            messages.error(request, "Community not found")
    
    return redirect('list_shepherds')


# ================================================================================= #
#                                   Api View Functions                              #
# ================================================================================= #
def api_get_members(request, user_id):
    if user_id is not None:
        try:
            user = User.objects.get(id=user_id)
        except:
            user = None

        if user is not None:
            members = Member.objects.active()
            shepherds = CommunityLeader.objects.all()
            ministry = Ministry.objects.all()

            data = {
                "STATUS": "OK",
                "members": members,
                "shepherds": shepherds,
                "ministry": ministry
            }

        else:
            data = {"STATUS": "INVALID", "ERROR_TYPE": "AUTHENTICATION PROBLEM", "STATUS_CODE": -1}
    else:
        data = {"STATUS": "INVALID", "ERROR_TYPE": "USER NOT LOGGED IN", "STATUS_CODE": 0}

    return JsonResponse(data, content_type="Application/json", safe=False)


def api_create_member(request, user_id):
    data = {}
    if user_id is not None:
        try:
            user = User.objects.get(id=user_id)
        except:
            user = None
        if user is not None:
            if request.method == "POST":
                form = MemberForm(request.POST, request.FILES or None)
                if form.is_valid():
                    member = form.save(commit=False)
                    member.save()
                    data = {"STATUS": "OK", "MEMBER_ID": member.pk}
                    return JsonResponse(data, content_type="Application/json", safe=False)
                else:
                    data = {"STATUS": "INVALID"}
        else:
            data = {"STATUS": "INVALID", "ERROR_TYPE": "AUTHENTICATION PROBLEM", "STATUS_CODE": -1}
    else:
        data = {"STATUS": "INVALID", "ERROR_TYPE": "USER NOT LOGGED IN", "STATUS_CODE": 0}

    return JsonResponse(data, content_type="Application/json", safe=False)


def api_get_shepherds(request):
    shepherds = CommunityLeader.objects.all()
    data = {"shepherds": shepherds}
    return JsonResponse(data, content_type="Application/json", safe=False)


def api_create_shepherd(request):
    if request.method == "POST":
        form = ShepherdForm(request.POST, request.FILES or None)
        if form.is_valid():
            shepherd = form.save(commit=False)
            shepherd.save()
            data = {"STATUS": "OK", "SHEPHERD_ID": shepherd.pk}
            return JsonResponse(data, content_type="Application/json", safe=False)
        else:
            data = {"STATUS": "INVALID"}
            return JsonResponse(data, content_type="Application/json", safe=False)


def api_edit_shepherd(request, pk):
    if request.method == "POST":
        shepherd = get_object_or_404(CommunityLeader, pk=pk)
        form = ShepherdForm(request.POST or None, instance=shepherd)
        if form.is_valid():
            form.save()
            data = {"STATUS": "OK", "CODE": 0}
        else:
            data = {"STATUS": "INVALID", "CODE": -1}
        return JsonResponse(data, content_type="Application/json", safe=False)


def api_delete_shepherd(request, pk):
    if request.method == "POST":
        shepherd = get_object_or_404(CommunityLeader, pk=pk)
        form = ShepherdForm(request.POST or None, instance=shepherd)
        if form.is_valid():
            form.delete()
            data = {"STATUS": "OK", "CODE": 0}
        else:
            data = {"STATUS": "INVALID", "CODE": -1}
        return JsonResponse(data, content_type="Application/json", safe=False)


def api_get_ministry(request):
    ministries = Ministry.objects.all()
    data = {"ministries": ministries}
    return JsonResponse(data, content_type="Application/json", safe=False)


def api_edit_ministry(request, pk):
    if request.method == "POST":
        ministry = get_object_or_404(Ministry, pk=pk)
        form = MinistryForm(request.POST or None, instance=ministry)
        if form.is_valid():
            form.save()
            data = {"STATUS": "OK", "CODE": 0}
        else:
            data = {"STATUS": "INVALID"}
        return JsonResponse(data, content_type="Application/json", safe=Fale)


# def api_delete_ministry(request, pk):



def api_create_ministry(request):
    if request.method == "POST":
        form = MinistryForm(request.POST, request.FILES or None)
        if form.is_valid():
            ministry = form.save(commit=False)
            ministry.save()
            data = {"STATUS": "OK", "MINISTRY_ID": ministry.pk}
            return JsonResponse(data, content_type="Application/json", safe=False)
        else:
            data = {"STATUS": "INVALID"}
            return JsonResponse(data, content_type="Application/json", safe=False)


# def api_get_members_status(request, status)