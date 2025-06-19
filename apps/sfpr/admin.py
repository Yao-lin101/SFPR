from django.contrib import admin
from .models import Player, Record


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'game_id', 'server_name', 'created_at', 'views_count')
    list_filter = ('server', 'created_at')
    search_fields = ('nickname', 'game_id')
    readonly_fields = ('id', 'created_at', 'updated_at', 'views_count')
    date_hierarchy = 'created_at'


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('player', 'submitter', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('player__nickname', 'player__game_id', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    actions = ['approve_records', 'reject_records']
    
    def approve_records(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} 条记录已批准。')
    approve_records.short_description = "批准选中的神人事迹"
    
    def reject_records(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} 条记录已拒绝。')
    reject_records.short_description = "拒绝选中的神人事迹"

