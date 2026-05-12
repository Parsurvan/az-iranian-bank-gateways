from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('azbankgateways', '0006_alter_bank_bank_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bank',
            name='bank_type',
            field=models.CharField(
                choices=[
                    ('BMI', 'BMI'),
                    ('SEP', 'SEP'),
                    ('ZARINPAL', 'Zarinpal'),
                    ('ZIBAL', 'Zibal'),
                    ('BAHAMTA', 'Bahamta'),
                    ('MELLAT', 'Mellat'),
                    ('IRANDARGAH', 'IranDargah'),
                    ('ASANPARDAKHT', 'AsanPardakht'),
                    ('MOCK', 'Mock (sandbox)'),
                ],
                max_length=50,
                verbose_name='Bank',
            ),
        ),
    ]
