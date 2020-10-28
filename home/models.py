from django.db import models

from modelcluster.fields import ParentalKey

from modelcluster.tags import ClusterTaggableManager

from wagtail.snippets.models import register_snippet
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel
from wagtail.images.models import AbstractImage
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from datetime import datetime

# from wagtail.search import index
from taggit.models import TaggedItemBase, Tag as TaggitTag


class HomePage(Page):
    is_creatable = False
    about_us_text = RichTextField(blank=True)
    content_panels = Page.content_panels + [
        FieldPanel(
            "about_us_text",
        ),
        InlinePanel("gallery_images", label="Gallery images"),
    ]
    subpage_types = []

    def get_context(self, request, *args, **kwargs):
        context = super(HomePage, self).get_context(request, *args, **kwargs)
        context["tournaments"] = Tournament.objects.all().live().order_by("-pk")[:5]
        context["featured_tournaments"] = (
            Tournament.objects.filter(featured=True).live().order_by("-pk")[:2]
        )
        context["blog_page"] = BlogPage.objects.first()
        context["tournament_list_page"] = TournamentList.objects.first()

        return context


class GalleryImage(Orderable):
    page = ParentalKey(
        HomePage, on_delete=models.CASCADE, related_name="gallery_images"
    )
    image = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.CASCADE, related_name="+"
    )
    caption = models.CharField(blank=True, max_length=250)
    landscape = models.BooleanField(default=False)
    protrait = models.BooleanField(default=False)
    object_position = models.CharField(
        max_length=25, null=True, default=None, blank=True
    )
    custom_css = models.CharField(max_length=45, null=True, default=None, blank=True)
    panels = [
        ImageChooserPanel("image"),
        FieldPanel("caption"),
        FieldPanel("landscape"),
        FieldPanel("protrait"),
        FieldPanel("object_position"),
        FieldPanel("custom_css"),
    ]


class TournamentList(Page):
    is_creatable = False
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel(
            "body",
        ),
    ]
    subpage_types = ["Tournament"]
    # parent_page_type = ["HomePage"]

    def get_context(self, request, *args, **kwargs):
        context = super(TournamentList, self).get_context(request, *args, **kwargs)
        context["tournaments"] = Tournament.objects.all().live().order_by("-pk")
        context["featured_tournaments"] = (
            Tournament.objects.filter(featured=True).live().order_by("-pk")
        )

        return context


class Tournament(Page):
    tournament_name = models.CharField(max_length=60)
    tournament_date = models.DateField(default=datetime.now)
    poster = models.ImageField(upload_to="tournaments/", blank=True, null=True)
    information = RichTextField(blank=True)
    featured = models.BooleanField(default=False)
    tags = ClusterTaggableManager(through="TournamentTag", blank=True)
    content_panels = Page.content_panels + [
        FieldPanel("tournament_name"),
        FieldPanel("tournament_date"),
        FieldPanel("featured"),
        FieldPanel("poster"),
        FieldPanel("information"),
        FieldPanel("tags"),
    ]

    subpage_types = []
    parent_page_type = ["TournamentList"]


class BlogPage(RoutablePageMixin, Page):
    description = models.CharField(
        max_length=255,
        blank=True,
    )

    content_panels = Page.content_panels + [FieldPanel("description", classname="full")]

    subpage_types = ["PostPage"]
    # parent_page_type = ["HomePage"]

    def get_context(self, request, *args, **kwargs):
        context = super(BlogPage, self).get_context(request, *args, **kwargs)
        context["posts"] = self.posts
        context["blog_page"] = self
        context["search_type"] = getattr(self, "search_type", "")
        context["search_term"] = getattr(self, "search_term", "")
        return context

    def get_posts(self):
        return PostPage.objects.descendant_of(self).live()

    @route(r"^tag/(?P<tag>[-\w]+)/$")
    def post_by_tag(self, request, tag, *args, **kwargs):
        self.search_type = "tag"
        self.search_term = tag
        self.posts = self.get_posts().filter(tags__slug=tag)
        return Page.serve(self, request, *args, **kwargs)

    @route(r"^$")
    def post_list(self, request, *args, **kwargs):
        self.posts = self.get_posts()
        return Page.serve(self, request, *args, **kwargs)

    @route(r"^search/$")
    def post_search(self, request, *args, **kwargs):
        search_query = request.GET.get("q", None)
        self.posts = self.get_posts()
        if search_query:
            self.posts = self.posts.filter(body__contains=search_query)
            self.search_term = search_query
            self.search_type = "search"
        return Page.serve(self, request, *args, **kwargs)


class PostPage(Page):
    body = RichTextField(blank=True)
    date = models.DateTimeField(verbose_name="Post date", default=datetime.today)
    tags = ClusterTaggableManager(through="BlogPageTag", blank=True)
    feed_image = models.ImageField(upload_to="posts/", blank=True, null=True)
    content_panels = Page.content_panels + [
        FieldPanel("body", classname="full"),
        FieldPanel("tags"),
    ]
    settings_panels = Page.settings_panels + [
        FieldPanel("date"),
    ]
    subpage_types = []
    parent_page_type = ["BlogPage"]

    search_fields = Page.search_fields + [
        index.SearchField("title"),
        index.SearchField("body"),
    ]

    @property
    def blog_page(self):
        return self.get_parent().specific

    def get_context(self, request, *args, **kwargs):
        context = super(PostPage, self).get_context(request, *args, **kwargs)
        context["blog_page"] = self.blog_page
        return context


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey("PostPage", related_name="post_tags")


class TournamentTag(TaggedItemBase):
    content_object = ParentalKey("Tournament", related_name="post_tags")


@register_snippet
class Tag(TaggitTag):
    class Meta:
        proxy = True