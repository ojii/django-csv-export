from datetime import datetime
from django.contrib import admin
from django.contrib.admin.util import unquote
from django.http import HttpResponse
from django.utils.functional import update_wrapper
import csv
import re

class CSVExportableAdmin(admin.ModelAdmin):
    csv_export_url = '~csv/'
    csv_export_dialect = 'excel'
    csv_export_fmtparam = {
       'delimiter': ',',
       'quotechar': '\\',
       'quoting': csv.QUOTE_MINIMAL,
    }
    change_list_template = 'csvexport/change_list.html'
    
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.module_name
        
        urlpatterns = patterns('',
            url(r'^%s$' % re.escape(self.csv_export_url),
                wrap(self.csv_export),
                name='%s_%s_csv_export' % info),
        )
        urlpatterns += super(CSVExportableAdmin, self).get_urls()
        return urlpatterns
    
    def csv_export(self, request):
        fields = self.get_csv_export_fields(request)
        headers = [f[1] for f in fields]
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s' % self.get_csv_export_filename(request)
        writer = csv.writer(response, self.csv_export_dialect, **self.csv_export_fmtparam)
        writer.writerow(headers)
        for row in self.model.objects.all():
            csvrow = [f.encode('utf-8') if isinstance(f, unicode) else f for f in [self.csv_resolve_field(row, f) for f in fields]]
            writer.writerow(csvrow)    
        return response
        
    def get_csv_export_fields(self, request):
        """
        Return a sequence of tuples which should be included in the export.
        """
        return [(f.name, f.verbose_name) for f in self.model._meta.fields]
    
    def get_csv_export_filename(self, request):
        ts = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        return '%s_%s_%s_export.csv' % (ts, self.model._meta.app_label, self.model._meta.module_name)

    def csv_resolve_field(self, row, fieldname):
        if isinstance(row, basestring):
            return getattr(row, fieldname)
        else:
            obj = row
            for bit in fieldname:
                obj = getattr(obj, bit)
            return obj
        
    def changelist_view(self, request, extra_context=None):
        extra_context = {'csv_export_url': self.csv_export_url}
        return super(CSVExportableAdmin, self).changelist_view(request, extra_context)