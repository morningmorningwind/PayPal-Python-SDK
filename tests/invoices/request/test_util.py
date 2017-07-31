import random
import string

import paypalrestsdk


def invoice_template_attributes():
    return {
        "name": "Hours Template_" + "".join([random.choice(string.ascii_uppercase) for i in range(5)]),
        "default": True,
        "unit_of_measure": "HOURS",
        "template_data": {
            "items": [{
                "name": "Nutri Bullet",
                "quantity": 1,
                "unit_price": {
                    "currency": "USD",
                    "value": "50.00"
                }
            }
            ],
            "merchant_info": {
                "email": "team-dx-clients-facilitator@getbraintree.com"
            },
            "tax_calculated_after_discount": False,
            "tax_inclusive": False,
            "note": "Thank you for your business.",
            "logo_url": "https://pics.paypal.com/v1/images/redDot.jpeg"
        },
        "settings": [
            {
                "field_name": "items.date",
                "display_preference": {
                    "hidden": True
                }
            },
            {
                "field_name": "custom",
                "display_preference": {
                    "hidden": True
                }
            }
        ]
    }


def deleteTemplate(client, template_id):
    return client.execute(paypalrestsdk.TemplateDeleteRequest(template_id))


def createTemplate(client):
    request = paypalrestsdk.TemplateCreateRequest()
    request.body(invoice_template_attributes())

    response = client.execute(request)
    return response, lambda: deleteTemplate(client, response.result.template_id)


def createInvoice(client):
    invoice_request = paypalrestsdk.InvoiceCreateRequest()
    invoice_request.body({
        "merchant_info": {
            "email": "team-dx-clients-facilitator@getbraintree.com"
        }
    })

    return client.execute(invoice_request)


def sendInvoice(client):
    invoice_response = createInvoice(client)
    invoice_send_request = paypalrestsdk.InvoiceSendRequest(invoice_response.result.id)
    invoice_send_request.notifyMerchant(True)

    return client.execute(invoice_send_request), invoice_response.result.id


def getInvoice(client, id):
    return client.execute(paypalrestsdk.InvoiceGetRequest(id))


def createInvoicePayment(client, invoice_id=None, method="CASH"):
    if not invoice_id:
        invoice_send_response, invoice_id = sendInvoice(client)

    request = paypalrestsdk.InvoiceRecordPaymentRequest(invoice_id)
    request.body({
        "method": method,
        "date": "2017-07-11 00:01:00 PST",
        "amount": {
            "value": "10",
            "currency": "USD"
        }
    })

    return client.execute(request), invoice_id

def createInvoiceRefund(client):
    invoice_send_response, id = sendInvoice(client)

    createInvoicePayment(client, invoice_id=id)

    request = paypalrestsdk.InvoiceRecordRefundRequest(id)
    request.body({
        "amount": {
            "currency": "USD",
            "value": "10"
        }
    })

    return client.execute(request), id
