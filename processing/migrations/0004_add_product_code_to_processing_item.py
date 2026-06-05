from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('processing', '0003_sync_processing_item_columns'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE processing_processingticketitem
                ADD COLUMN product_code varchar(50);
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]