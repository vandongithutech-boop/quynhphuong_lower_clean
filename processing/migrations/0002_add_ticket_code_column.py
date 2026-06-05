from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('processing', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE processing_processingticket
                ADD COLUMN ticket_code varchar(50);
            """,
            reverse_sql="""
                ALTER TABLE processing_processingticket
                DROP COLUMN ticket_code;
            """
        ),
        migrations.RunSQL(
            sql="""
                UPDATE processing_processingticket
                SET ticket_code = 'SCOLD' || id
                WHERE ticket_code IS NULL;
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
    ]