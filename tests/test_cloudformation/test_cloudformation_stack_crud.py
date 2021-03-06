from __future__ import unicode_literals

import json

import boto
import boto.cloudformation
import sure  # noqa
# Ensure 'assert_raises' context manager support for Python 2.6
import tests.backport_assert_raises  # noqa
from nose.tools import assert_raises

from moto import mock_cloudformation
from moto.cloudformation.exceptions import ValidationError

dummy_template = {
    "AWSTemplateFormatVersion": "2010-09-09",
    "Description": "Stack 1",
    "Resources": {},
}

dummy_template2 = {
    "AWSTemplateFormatVersion": "2010-09-09",
    "Description": "Stack 2",
    "Resources": {},
}

dummy_template_json = json.dumps(dummy_template)
dummy_template_json2 = json.dumps(dummy_template2)


@mock_cloudformation
def test_create_stack():
    conn = boto.connect_cloudformation()
    conn.create_stack(
        "test_stack",
        template_body=dummy_template_json,
    )

    stack = conn.describe_stacks()[0]
    stack.stack_name.should.equal('test_stack')
    stack.get_template().should.equal(dummy_template)


@mock_cloudformation
def test_creating_stacks_across_regions():
    west1_conn = boto.cloudformation.connect_to_region("us-west-1")
    west1_conn.create_stack("test_stack", template_body=dummy_template_json)

    west2_conn = boto.cloudformation.connect_to_region("us-west-2")
    west2_conn.create_stack("test_stack", template_body=dummy_template_json)

    list(west1_conn.describe_stacks()).should.have.length_of(1)
    list(west2_conn.describe_stacks()).should.have.length_of(1)


@mock_cloudformation
def test_create_stack_with_notification_arn():
    conn = boto.connect_cloudformation()
    conn.create_stack(
        "test_stack_with_notifications",
        template_body=dummy_template_json,
        notification_arns='arn:aws:sns:us-east-1:123456789012:fake-queue'
    )

    stack = conn.describe_stacks()[0]
    [n.value for n in stack.notification_arns].should.contain('arn:aws:sns:us-east-1:123456789012:fake-queue')


@mock_cloudformation
def test_describe_stack_by_name():
    conn = boto.connect_cloudformation()
    conn.create_stack(
        "test_stack",
        template_body=dummy_template_json,
    )

    stack = conn.describe_stacks("test_stack")[0]
    stack.stack_name.should.equal('test_stack')


@mock_cloudformation
def test_describe_stack_by_stack_id():
    conn = boto.connect_cloudformation()
    conn.create_stack(
        "test_stack",
        template_body=dummy_template_json,
    )

    stack = conn.describe_stacks("test_stack")[0]
    stack_by_id = conn.describe_stacks(stack.stack_id)[0]
    stack_by_id.stack_id.should.equal(stack.stack_id)
    stack_by_id.stack_name.should.equal("test_stack")


@mock_cloudformation
def test_describe_deleted_stack():
    conn = boto.connect_cloudformation()
    conn.create_stack(
        "test_stack",
        template_body=dummy_template_json,
    )

    stack = conn.describe_stacks("test_stack")[0]
    stack_id = stack.stack_id
    conn.delete_stack(stack.stack_id)
    stack_by_id = conn.describe_stacks(stack_id)[0]
    stack_by_id.stack_id.should.equal(stack.stack_id)
    stack_by_id.stack_name.should.equal("test_stack")
    stack_by_id.stack_status.should.equal("DELETE_COMPLETE")


@mock_cloudformation
def test_get_template_by_name():
    conn = boto.connect_cloudformation()
    conn.create_stack(
        "test_stack",
        template_body=dummy_template_json,
    )

    template = conn.get_template("test_stack")
    template.should.equal(dummy_template)


@mock_cloudformation
def test_list_stacks():
    conn = boto.connect_cloudformation()
    conn.create_stack(
        "test_stack",
        template_body=dummy_template_json,
    )
    conn.create_stack(
        "test_stack2",
        template_body=dummy_template_json,
    )

    stacks = conn.list_stacks()
    stacks.should.have.length_of(2)
    stacks[0].template_description.should.equal("Stack 1")


@mock_cloudformation
def test_delete_stack_by_name():
    conn = boto.connect_cloudformation()
    conn.create_stack(
        "test_stack",
        template_body=dummy_template_json,
    )

    conn.list_stacks().should.have.length_of(1)
    conn.delete_stack("test_stack")
    conn.list_stacks().should.have.length_of(0)


@mock_cloudformation
def test_delete_stack_by_id():
    conn = boto.connect_cloudformation()
    stack_id = conn.create_stack(
        "test_stack",
        template_body=dummy_template_json,
    )

    conn.list_stacks().should.have.length_of(1)
    conn.delete_stack(stack_id)
    conn.list_stacks().should.have.length_of(0)
    with assert_raises(ValidationError):
        conn.describe_stacks("test_stack")

    conn.describe_stacks(stack_id).should.have.length_of(1)


@mock_cloudformation
def test_bad_describe_stack():
    conn = boto.connect_cloudformation()
    with assert_raises(ValidationError):
        conn.describe_stacks("bad_stack")


# @mock_cloudformation
# def test_update_stack():
#     conn = boto.connect_cloudformation()
#     conn.create_stack(
#         "test_stack",
#         template_body=dummy_template_json,
#     )

#     conn.update_stack("test_stack", dummy_template_json2)

#     stack = conn.describe_stacks()[0]
#     stack.get_template().should.equal(dummy_template2)
