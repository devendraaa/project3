from django.contrib import admin

from home.models import Login
from home.models import sen_locc
from home.models import final_sens
from home.models import db_sens
from home.models import hospital_name
from home.models import hospital_db

# Register your models here.
admin.site.register(Login)
admin.site.register(sen_locc)
admin.site.register(final_sens)
admin.site.register(db_sens)
admin.site.register(hospital_name)
admin.site.register(hospital_db)





