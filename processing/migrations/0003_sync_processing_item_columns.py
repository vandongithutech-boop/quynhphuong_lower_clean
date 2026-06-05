from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
    ('processing', '0002_add_ticket_code_column'),
]

    operations = [

        migrations.RunSQL(
            sql="""
                ALTER TABLE processing_processingticketitem
                ADD COLUMN raw_stock_id integer;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),

        migrations.RunSQL(
            sql="""
                ALTER TABLE processing_processingticketitem
                ADD COLUMN product_group varchar(10);
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),

        migrations.RunSQL(
            sql="""
                ALTER TABLE processing_processingticketitem
                ADD COLUMN supplier_code varchar(50);
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),

        migrations.RunSQL(
            sql="""
                ALTER TABLE processing_processingticketitem
                ADD COLUMN received_date datetime;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]