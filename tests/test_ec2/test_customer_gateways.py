from __future__ import unicode_literals
import boto
import sure  # noqa

from moto import mock_ec2


@mock_ec2
def test_customer_gateways():
    conn = boto.connect_vpc('the_key', 'the_secret')

    customer_gateway = conn.create_customer_gateway(
        type='ipsec.1',
        bgp_asn=65000,
        ip_address='10.0.0.1',
    )
    customer_gateway.should_not.be.none
    customer_gateway.id.should.match(r'cgw-\w+')
    customer_gateway.type.should.equal('ipsec.1')
    customer_gateway.state.should.equal('available')
    customer_gateway.ip_address.should.equal('10.0.0.1')
    customer_gateway.bgp_asn.should.equal(65000)

@mock_ec2
def test_describe_customer_gateway():
    conn = boto.connect_vpc('the_key', 'the_secret')
    customer_gateway = conn.create_customer_gateway(
        type='ipsec.1',
        bgp_asn=65000,
        ip_address='10.0.0.1',
    )

    vgws = conn.get_all_customer_gateways()
    vgws.should.have.length_of(1)

    gateway = vgws[0]
    gateway.id.should.match(r'cgw-\w+')
    gateway.id.should.equal(customer_gateway.id)
    customer_gateway.type.should.equal('ipsec.1')
    customer_gateway.state.should.equal('available')
    customer_gateway.ip_address.should.equal('10.0.0.1')
    customer_gateway.bgp_asn.should.equal(65000)

@mock_ec2
def test_customer_gateway_tagging():
    conn = boto.connect_vpc('the_key', 'the_secret')
    customer_gateway = conn.create_customer_gateway(
        type='ipsec.1',
        bgp_asn=65000,
        ip_address='10.0.0.1',
    )
    customer_gateway.add_tag("a key", "some value")

    tag = conn.get_all_tags()[0]
    tag.name.should.equal("a key")
    tag.value.should.equal("some value")

    # Refresh the subnet
    customer_gateway = conn.get_all_customer_gateways()[0]
    customer_gateway.tags.should.have.length_of(1)
    customer_gateway.tags["a key"].should.equal("some value")

@mock_ec2
def test_delete_customer_gateway():
    conn = boto.connect_vpc('the_key', 'the_secret')
    customer_gateway = conn.create_customer_gateway(
        type='ipsec.1',
        bgp_asn=65000,
        ip_address='10.0.0.1',
    )

    conn.delete_customer_gateway(customer_gateway.id)
    vgws = conn.get_all_customer_gateways()
    vgws.should.have.length_of(0)