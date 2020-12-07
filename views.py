from django.shortcuts import render,Http404, get_object_or_404, redirect
from django.views.generic import CreateView
from .models import author, category, article, comment
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .forms import createForm, registerUser, createAuthor, categoryForm, commentForm
from django.contrib import messages
from django.views import View



# Create your views here.
class index(View):
    template_name ="index.html"

    def get(self, request):
        post = article.objects.all()
        search = request.GET.get( 'q' )
        if search:
            post = post.filter(
                Q( title__icontains=search ) |
                Q( body__icontains=search )
            )
        paginator = Paginator( post, 3 )  # Show 25 contacts per page

        page = request.GET.get( 'page' )
        total_article = paginator.get_page( page )
        context = {
            "post": total_article
        }
        return render( request,self.template_name, context )


def getauthor( request, name):
        post_author = get_object_or_404( User, username=name )
        auth = get_object_or_404( author, name=post_author.id )
        post = article.objects.filter( article_author=auth.id )
        context = {
            "auth": auth,
            "post": post
        }
        return render( request,"profile.html", context )


def getsingle( request, id):
        post = get_object_or_404( article, pk=id )
        first = article.objects.first()
        last = article.objects.last()
        getComment = comment.objects.filter( post=id )
        related = article.objects.filter( category=post.category ).exclude( id=id )[:4]
        form = commentForm(request.POST or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.post = post
            instance.save()
        context = {
            "post": post,
            "first": first,
            "last": last,
            "related": related,
            "form": form,
            "commnet": getComment
        }
        return render( request, "single.html", context )


def getTopic(request,name):
        cat = get_object_or_404( category, name=name )
        post = article.objects.filter( category=cat.id )
        paginator = Paginator( post, 4 )  # Show 25 contacts per page

        page = request.GET.get( 'page' )
        total_article = paginator.get_page( page )
        return render( request, "category.html", {"post": total_article, "cat": cat} )


def getLogin(request):
       if request.user.is_authenticated:
           return redirect( 'Blog:index' )
       else:
           if request.method =="POST":
               user = request.POST.get( 'user' )
               password = request.POST.get( 'pass' )
               auth = authenticate( request, username=user, password=password )
               if auth is not None:
                   login( request, auth )
                   return redirect( 'Blog:index' )
               else:
                   messages.add_message( request, messages.ERROR, 'Username or Password mismatch' )
                   return redirect( "login.html" )
               return render(request, "login.html")


class LoginView( View ):
    template_name = "login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect( 'Blog:index' )
        return render( request, self.template_name )

    def post(self, request):
        user = request.POST.get( 'user' )
        password = request.POST.get( 'pass' )
        auth = authenticate( request, username=user, password=password )
        if auth is not None:
            login( request, auth )
            return redirect( 'Blog:index' )
        else:
            messages.add_message( request, messages.ERROR, 'Username or password mismatch' )
            return render( request, self.template_name )


def getLogout(request):
        logout( request )
        return redirect( 'Blog:index' )


def getcreate(request):
        if request.user.is_authenticated:
            u = get_object_or_404( author, name=request.user.id )
            form = createForm( request.POST or None, request.FILES or None )
            if form.is_valid():
                instance = form.save( commit=False )
                instance.article_author = u
                instance.save()
                return redirect( 'Blog:index' )
            return render( request, 'create.html', {"form": form} )
        else:
            return redirect( 'Blog:login' )

def getUpdate(request, pid):
            if request.user.is_authenticated:
                u = get_object_or_404( author, name=request.user.id )
                post = get_object_or_404( article, id=pid )
                form = createForm( request.POST or None, request.FILES or None, instance=post )
                if form.is_valid():
                    instance = form.save( commit=False )
                    instance.article_author = u
                    instance.save()
                    messages.success( request, 'Article is updated successfully' )
                    return redirect( 'Blog:profile' )
                return render( request, 'create.html', {"form": form} )
            else:
                return redirect( 'Blog:login' )

def getDelete(request, pid):
               if request.user.is_authenticated:
                   post = get_object_or_404( article, id=pid )
                   post.delete()
                   messages.warning(request, 'Article is deleted successfully')
                   return redirect( 'Blog:profile' )
               else:
                   return redirect( 'Blog:login' )



def getProfile(request):
         if request.user.is_authenticated:
             user = get_object_or_404( User, id=request.user.id )
             author_profile = author.objects.filter( name=user.id )
             if author_profile:
                 authorUser = get_object_or_404( author, name=request.user.id )
                 post = article.objects.filter( article_author=authorUser.id )
                 return render( request, 'logged_in_profile.html', {"post": post, "user": authorUser} )
             else:
                 form = createAuthor( request.POST or None, request.FILES or None )
                 if form.is_valid():
                     instance = form.save( commit=False )
                     instance.name = user
                     instance.save()
                     messages.success(request, 'Author profile is created successfully')
                     return redirect( 'Blog:profile' )
                 return render( request, 'createauthor.html', {"form": form} )
         else:

             return redirect( 'Blog:login' )


class RegistersView(View):
    template_name = 'register.html'
    form = registerUser

    def get(self, request):
        return render(request, self.template_name, {"form": self.form})

    def post(self, request):
            instance = self.form.save( commit=False )
            instance.save()
            messages.success( request, 'Registration successfully completed' )
            return redirect( 'Blog:login' )


def getCategory(request):
        query = category.objects.all()
        return render( request, 'topics.html', {"topics": query} )

def createTopic(request):
    if request.uer.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
              form = categoryForm( request.POST or None )
              if form.is_valid():
                   instance = form.save( commit=False )
                   instance.save()
                   messages.success( request, 'topic is created!')
                   return redirect( 'Blog:category')
              return render( request, 'create_topics.html', {"form": form} )
        else:
               raise Http404('You are not authorized to access this page')
    else:
                 return redirect('Blog:login')

class createTopicView(CreateView):

    model = category
    template_name = 'create_topics.html'
    fields = ('name',)
    success_url = '/topics'