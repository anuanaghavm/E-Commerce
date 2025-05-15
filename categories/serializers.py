from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'parent', 'description', 'image', 
                 'meta_title', 'meta_description', 'is_active', 'children',
                 'created_at', 'updated_at')
        read_only_fields = ('slug', 'created_at', 'updated_at')
    
    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.all(), many=True).data
        return None
    
    def validate_parent(self, value):
        if value and value.parent == self.instance:
            raise serializers.ValidationError("A category cannot be its own parent.")
        return value 