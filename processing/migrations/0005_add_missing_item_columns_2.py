from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('processing', '0004_add_product_code_to_processing_item'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE processing_processingticketitem
                ADD COLUMN unit varchar(100);
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="""
                ALTER TABLE processing_processingticketitem
                ADD COLUMN flower_grade varchar(100);
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
       
        
        
    ]