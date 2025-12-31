from rest_framework import serializers
from blog.models import Post,Category
from django.urls import reverse
from accounts.models import Profile
from django.utils.text import Truncator
#convert data into jason so we can screen it!#


# class PostSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255)
#     author = serializers.CharField(max_length=255)

#we use serializer when we need more control, customization, or are working with non-model data!#
#but we use ModelSerializer when we are dealing with models in a standard CRUD context!#
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name','id']

    def validate_name(self, value):
        name = value.strip()
        qs = Category.objects.filter(name__iexact=name)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Category with this name already exists.")
        return name

class PostSerializer(serializers.ModelSerializer):
    urls = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()
    author_id = serializers.IntegerField(read_only=True)
    categories = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Category.objects.all())
    categories_info = CategorySerializer(source='categories', many=True, read_only=True)
    excerpt = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = ['id','author_id','author_name','image','title','excerpt','content','categories','categories_info','status','urls','created_date','published_date','counted_view']
        read_only_fields = ['author_name']

    def get_urls(self,obj):
        request = self.context.get('request')
        relative_url = reverse('blog:api-v1:post-detail', args=[obj.pk])
        absolute_url = request.build_absolute_uri(relative_url) if request else None
        return {
            "relative": relative_url,
            "absolute": absolute_url,
        }
    
    def get_author_name(self,obj):
        return f'{obj.author.first_name} {obj.author.last_name}'
    
    def get_excerpt(self, obj):
        return Truncator(obj.content).words(30, truncate="...")
    
    #to_representation is used to only and only for showing the data differently!(not editing!)#
    def to_representation(self, instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)
        if request.parser_context.get('kwargs').get('pk'):#this means that request is asking for post details,not post list!#
            rep.pop('urls')#for showing the detail part of api!#
        else:
            rep.pop('content')#for showing the list part of api!#
        return rep
    
    def create(self, validated_data):#check that for creating the post,user is assigned automatically! #
        validated_data['author'] = Profile.objects.get(user__id = self.context.get('request').user.id)
        return super().create(validated_data)

