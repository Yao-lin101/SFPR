from django.contrib import admin
from .models import Server, Partner


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'region')
    search_fields = ('name', 'region')


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'game_id', 'server', 'status', 'created_at', 'views_count')
    list_filter = ('status', 'server', 'created_at')
    search_fields = ('nickname', 'game_id', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at', 'views_count')
    date_hierarchy = 'created_at'
    actions = ['approve_partners', 'reject_partners']
    
    def approve_partners(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} 条记录已批准。')
    approve_partners.short_description = "批准选中的神人记录"
    
    def reject_partners(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} 条记录已拒绝。')
    reject_partners.short_description = "拒绝选中的神人记录"
