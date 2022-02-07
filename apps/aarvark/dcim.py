# C3000 (tall-models)
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey


class ComponentModel(PrimaryModel):
    device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.CASCADE,
        related_name='%(class)ss'
    )
    name = models.CharField(
        max_length=64
    )
    _name = NaturalOrderingField(
        target_field='name',
        max_length=100,
        blank=True
    )
    label = models.CharField(
        max_length=64,
        blank=True,
        help_text="Physical label"
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )

    class Meta:
        abstract = True


class LinkTermination(models.Model):
    cable = models.ForeignKey(
        to='dcim.Cable',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True
    )
    _link_peer_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True
    )
    _link_peer_id = models.PositiveIntegerField(
        blank=True,
        null=True
    )
    _link_peer = GenericForeignKey(
        ct_field='_link_peer_type',
        fk_field='_link_peer_id'
    )
    mark_connected = models.BooleanField(
        default=False,
        help_text="Treat as if a cable is connected"
    )

    # Generic relations to Cable. These ensure that an attached Cable is deleted if the terminated object is deleted.
    _cabled_as_a = GenericRelation(
        to='dcim.Cable',
        content_type_field='termination_a_type',
        object_id_field='termination_a_id'
    )
    _cabled_as_b = GenericRelation(
        to='dcim.Cable',
        content_type_field='termination_b_type',
        object_id_field='termination_b_id'
    )

    class Meta:
        abstract = True


class PathEndpoint(models.Model):

    _path = models.ForeignKey(
        to='dcim.CablePath',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        abstract = True


class ConsolePort(ComponentModel, LinkTermination, PathEndpoint):
    type = models.CharField(
        max_length=50,
        choices=ConsolePortTypeChoices,
        blank=True,
        help_text='Physical port type'
    )
    speed = models.PositiveIntegerField(
        choices=ConsolePortSpeedChoices,
        blank=True,
        null=True,
        help_text='Port speed in bits per second'
    )

    clone_fields = ['device', 'type', 'speed']

    class Meta:
        ordering = ('device', '_name')
        unique_together = ('device', 'name')

    def get_absolute_url(self):
        return reverse('dcim:consoleport', kwargs={'pk': self.pk})


class ConsoleServerPort(ComponentModel, LinkTermination, PathEndpoint):

    type = models.CharField(
        max_length=50,
        choices=ConsolePortTypeChoices,
        blank=True,
        help_text='Physical port type'
    )
    speed = models.PositiveIntegerField(
        choices=ConsolePortSpeedChoices,
        blank=True,
        null=True,
        help_text='Port speed in bits per second'
    )

    clone_fields = ['device', 'type', 'speed']

    class Meta:
        ordering = ('device', '_name')
        unique_together = ('device', 'name')

    def get_absolute_url(self):
        return reverse('dcim:consoleserverport', kwargs={'pk': self.pk})


class PowerPort(ComponentModel, LinkTermination, PathEndpoint):

    type = models.CharField(
        max_length=50,
        choices=PowerPortTypeChoices,
        blank=True,
        help_text='Physical port type'
    )
    maximum_draw = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text="Maximum power draw (watts)"
    )
    allocated_draw = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text="Allocated power draw (watts)"
    )

    clone_fields = ['device', 'maximum_draw', 'allocated_draw']

    class Meta:
        ordering = ('device', '_name')
        unique_together = ('device', 'name')

    def get_absolute_url(self):
        return reverse('dcim:powerport', kwargs={'pk': self.pk})


class PowerOutlet(ComponentModel, LinkTermination, PathEndpoint):
   type = models.CharField(
        max_length=50,
        choices=PowerOutletTypeChoices,
        blank=True,
        help_text='Physical port type'
    )
    power_port = models.ForeignKey(
        to='dcim.PowerPort',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='poweroutlets'
    )
    feed_leg = models.CharField(
        max_length=50,
        choices=PowerOutletFeedLegChoices,
        blank=True,
        help_text="Phase (for three-phase feeds)"
    )

    clone_fields = ['device', 'type', 'power_port', 'feed_leg']

    class Meta:
        ordering = ('device', '_name')
        unique_together = ('device', 'name')


class BaseInterface(models.Model):
    enabled = models.BooleanField(
        default=True
    )
    mac_address = MACAddressField(
        null=True,
        blank=True,
        verbose_name='MAC Address'
    )
    mtu = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(INTERFACE_MTU_MIN),
            MaxValueValidator(INTERFACE_MTU_MAX)
        ],
        verbose_name='MTU'
    )
    mode = models.CharField(
        max_length=50,
        choices=InterfaceModeChoices,
        blank=True
    )
    parent = models.ForeignKey(
        to='self',
        on_delete=models.SET_NULL,
        related_name='child_interfaces',
        null=True,
        blank=True,
        verbose_name='Parent interface'
    )
    bridge = models.ForeignKey(
        to='self',
        on_delete=models.SET_NULL,
        related_name='bridge_interfaces',
        null=True,
        blank=True,
        verbose_name='Bridge interface'
    )

    class Meta:
        abstract = True


class Interface(ComponentModel, BaseInterface, LinkTermination, PathEndpoint):
    _name = NaturalOrderingField(
        target_field='name',
        naturalize_function=naturalize_interface,
        max_length=100,
        blank=True
    )
    lag = models.ForeignKey(
        to='self',
        on_delete=models.SET_NULL,
        related_name='member_interfaces',
        null=True,
        blank=True,
        verbose_name='Parent LAG'
    )
    type = models.CharField(
        max_length=50,
        choices=InterfaceTypeChoices
    )
    mgmt_only = models.BooleanField(
        default=False,
        verbose_name='Management only',
        help_text='This interface is used only for out-of-band management'
    )
    wwn = WWNField(
        null=True,
        blank=True,
        verbose_name='WWN',
        help_text='64-bit World Wide Name'
    )
    rf_role = models.CharField(
        max_length=30,
        choices=WirelessRoleChoices,
        blank=True,
        verbose_name='Wireless role'
    )
    rf_channel = models.CharField(
        max_length=50,
        choices=WirelessChannelChoices,
        blank=True,
        verbose_name='Wireless channel'
    )
    rf_channel_frequency = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Channel frequency (MHz)'
    )
    rf_channel_width = models.DecimalField(
        max_digits=7,
        decimal_places=3,
        blank=True,
        null=True,
        verbose_name='Channel width (MHz)'
    )
    tx_power = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=(MaxValueValidator(127),),
        verbose_name='Transmit power (dBm)'
    )
    wireless_link = models.ForeignKey(
        to='wireless.WirelessLink',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True
    )
    wireless_lans = models.ManyToManyField(
        to='wireless.WirelessLAN',
        related_name='interfaces',
        blank=True,
        verbose_name='Wireless LANs'
    )
    untagged_vlan = models.ForeignKey(
        to='ipam.VLAN',
        on_delete=models.SET_NULL,
        related_name='interfaces_as_untagged',
        null=True,
        blank=True,
        verbose_name='Untagged VLAN'
    )
    tagged_vlans = models.ManyToManyField(
        to='ipam.VLAN',
        related_name='interfaces_as_tagged',
        blank=True,
        verbose_name='Tagged VLANs'
    )
    ip_addresses = GenericRelation(
        to='ipam.IPAddress',
        content_type_field='assigned_object_type',
        object_id_field='assigned_object_id',
        related_query_name='interface'
    )
    fhrp_group_assignments = GenericRelation(
        to='ipam.FHRPGroupAssignment',
        content_type_field='interface_type',
        object_id_field='interface_id',
        related_query_name='+'
    )

    clone_fields = ['device', 'parent', 'bridge', 'lag', 'type', 'mgmt_only']

    class Meta:
        ordering = ('device', CollateAsChar('_name'))
        unique_together = ('device', 'name')


class FrontPort(ComponentModel, LinkTermination):
    type = models.CharField(
        max_length=50,
        choices=PortTypeChoices
    )
    color = ColorField(
        blank=True
    )
    rear_port = models.ForeignKey(
        to='dcim.RearPort',
        on_delete=models.CASCADE,
        related_name='frontports'
    )
    rear_port_position = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(REARPORT_POSITIONS_MIN),
            MaxValueValidator(REARPORT_POSITIONS_MAX)
        ]
    )

    clone_fields = ['device', 'type']

    class Meta:
        ordering = ('device', '_name')
        unique_together = (
            ('device', 'name'),
            ('rear_port', 'rear_port_position'),
        )

    def get_absolute_url(self):
        return reverse('dcim:frontport', kwargs={'pk': self.pk})


class RearPort(ComponentModel, LinkTermination):
    type = models.CharField(
        max_length=50,
        choices=PortTypeChoices
    )
    color = ColorField(
        blank=True
    )
    positions = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(REARPORT_POSITIONS_MIN),
            MaxValueValidator(REARPORT_POSITIONS_MAX)
        ]
    )
    clone_fields = ['device', 'type', 'positions']

    class Meta:
        ordering = ('device', '_name')
        unique_together = ('device', 'name')

    def get_absolute_url(self):
        return reverse('dcim:rearport', kwargs={'pk': self.pk})


class DeviceBay(ComponentModel):
    """
    An empty space within a Device which can house a child device
    """
    installed_device = models.OneToOneField(
        to='dcim.Device',
        on_delete=models.SET_NULL,
        related_name='parent_bay',
        blank=True,
        null=True
    )

    clone_fields = ['device']

    class Meta:
        ordering = ('device', '_name')
        unique_together = ('device', 'name')

    def get_absolute_url(self):
        return reverse('dcim:devicebay', kwargs={'pk': self.pk})

    def clean(self):
        super().clean()

        # Validate that the parent Device can have DeviceBays
        if not self.device.device_type.is_parent_device:
            raise ValidationError("This type of device ({}) does not support device bays.".format(
                self.device.device_type
            ))

        # Cannot install a device into itself, obviously
        if self.device == self.installed_device:
            raise ValidationError("Cannot install a device into itself.")

        # Check that the installed device is not already installed elsewhere
        if self.installed_device:
            current_bay = DeviceBay.objects.filter(installed_device=self.installed_device).first()
            if current_bay and current_bay != self:
                raise ValidationError({
                    'installed_device': "Cannot install the specified device; device is already installed in {}".format(
                        current_bay
                    )
                })


class InventoryItem(MPTTModel, ComponentModel):
    parent = TreeForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='child_items',
        blank=True,
        null=True,
        db_index=True
    )
    manufacturer = models.ForeignKey(
        to='dcim.Manufacturer',
        on_delete=models.PROTECT,
        related_name='inventory_items',
        blank=True,
        null=True
    )
    part_id = models.CharField(
        max_length=50,
        verbose_name='Part ID',
        blank=True,
        help_text='Manufacturer-assigned part identifier'
    )
    serial = models.CharField(
        max_length=50,
        verbose_name='Serial number',
        blank=True
    )
    asset_tag = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Asset tag',
        help_text='A unique tag used to identify this item'
    )
    discovered = models.BooleanField(
        default=False,
        help_text='This item was automatically discovered'
    )

    objects = TreeManager()

    clone_fields = ['device', 'parent', 'manufacturer', 'part_id']

    class Meta:
        ordering = ('device__id', 'parent__id', '_name')
        unique_together = ('device', 'parent', 'name')

    def get_absolute_url(self):
        return reverse('dcim:inventoryitem', kwargs={'pk': self.pk})