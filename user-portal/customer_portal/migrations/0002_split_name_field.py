from django.db import migrations, models

def split_name_field(apps, schema_editor):
    # Get the historical version of the Customer model
    Customer = apps.get_model('customer_portal', 'Customer')
    
    # Loop through all existing customers
    for customer in Customer.objects.all():
        # Split the name field into parts
        name_parts = customer.name.split()
        
        # Set first_name and last_name
        if len(name_parts) == 1:
            # Only one name part
            customer.first_name = name_parts[0]
            customer.last_name = ""
        elif len(name_parts) == 2:
            # Two name parts (first and last)
            customer.first_name = name_parts[0]
            customer.last_name = name_parts[1]
        else:
            # More than two name parts
            customer.first_name = name_parts[0]
            customer.last_name = name_parts[-1]
            customer.middle_name = " ".join(name_parts[1:-1])
        
        # Set default gender (can be updated later)
        customer.gender = 'other'
        
        # Save the customer
        customer.save()

class Migration(migrations.Migration):

    dependencies = [
        ('customer_portal', '0001_initial'),
    ]

    operations = [
        # First, add the new fields with null=True
        migrations.AddField(
            model_name='customer',
            name='first_name',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='middle_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='last_name',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='gender',
            field=models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], max_length=10, null=True),
        ),
        
        # Run the data migration
        migrations.RunPython(split_name_field),
        
        # Make the fields required (except middle_name)
        migrations.AlterField(
            model_name='customer',
            name='first_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='customer',
            name='last_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='customer',
            name='gender',
            field=models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], max_length=10),
        ),
        
        # Remove the old name field
        migrations.RemoveField(
            model_name='customer',
            name='name',
        ),
    ]

