from rest_framework import serializers
from blog.models import Post,Category
from django.urls import reverse
from accounts.models import Profile
#convert data into jason so we can screen it!#


# class PostSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255)
#     author = serializers.CharField(max_length=255)

#we use serializer when we need more control, customization, or are working with non-model data!#
#but we use ModelSerializer when we are dealing with models in a standard CRUD context!#

class PostSerializer(serializers.ModelSerializer):
    urls = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()
    category = serializers.SlugRelatedField(many=False,slug_field='name',queryset=Category.objects.all())
    class Meta:
        model = Post
        fields = ['id','author_name','image','title','content','category','status','urls','created_date','published_date']
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

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name','id']