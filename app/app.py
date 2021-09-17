import boto3, json, time, os, logging, botocore, requests
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
session = boto3.Session()

def lambda_handler(event, context):
    logger.info(json.dumps(event))
    userKeySecretARN = os.environ['NewRelicUserKeySecretARN']
    userKey = get_secret_value(userKeySecretARN)
    apps = get_newrelic_apps(userKey)
    attributeGroups = create_appregistry_attribute_groups()
    push_to_appregistry(apps, attributeGroups)
    
    return {
        'statusCode': 200,
        'body': json.dumps('success!')
    }
    
def get_secret_value(secret_arn):
    secretClient = session.client('secretsmanager')
    try:
        secret_response = secretClient.get_secret_value(
            SecretId=secret_arn
        )
        if 'SecretString' in secret_response:
            secret = json.loads(secret_response['SecretString'])['UserKey']
            return secret 
    
    except Exception as e:
        logger.error('Get Secret Failed: ' + str(e))

def pluck(dict0, include=None, exclude=None, prefix=''):
  return {prefix + k: str(v) for k, v in dict0.items() if (include is None or k in include)
    and (exclude is None or k not in exclude)}
    
def create_appregistry_attribute_group(appregistry, attributeGroup):
  import json
  from operator import itemgetter
  name, attributes, description = itemgetter('name', 'attributes', 'description')(attributeGroup)
  try:
     response = appregistry.create_attribute_group(
        name=name,
        description=description,
        attributes=json.dumps(attributes),
        clientToken=name
     )
     attributeGroupId = response['attributeGroup']['id']
     logger.info('created attribute group with id {}'.format(attributeGroupId))
     return attributeGroupId
  except Exception as e:
    if e.response['Error']['Code'] == 'ConflictException':
      logger.warn('ConflictException... {}'.format(e.response['Error']['Message']))
      return name
    logger.error('error... {}'.format(str(e)))

def create_appregistry_attribute_groups():
  import json
  appregistry = session.client('servicecatalog-appregistry')
  apm = json.load(open('NewRelic-APM-App.json'))
  browser = json.load(open('NewRelic-Browser-App.json'))
  mobile = json.load(open('NewRelic-Mobile-App.json'))
  attributeGroups = {}
  for attributeGroup in ( apm, browser, mobile ):
    attributeGroups[attributeGroup['attributes']['entityType']] = create_appregistry_attribute_group(appregistry, attributeGroup)
  logger.info('created attribute groups')
  return attributeGroups
    
def associate_attribute_group(appregistry, applicationId, attributeGroupId):
  try:
     appregistry.associate_attribute_group(
          application=applicationId,
          attributeGroup=attributeGroupId
     )
     logger.info(f'associated attribute group: {attributeGroupId} with application: {applicationId}')
  except Exception as e:
    logger.error('error... {}'.format(str(e)))
    
def create_appregistry_app(appregistry, name, tags, clientToken, retry=0):
  
  try:
     response = appregistry.create_application(
          name=name,
          tags=tags,
          clientToken=clientToken
     )
     applicationId = response['application']['id']
     logger.info('created application with id {}'.format(applicationId))
     return applicationId
  except Exception as e:
    if e.response['Error']['Code'] == 'ConflictException':
      logger.warn('ConflictException... {}'.format(e.response['Error']['Message']))
      return name
    logger.error('error... {}'.format(str(e)))
        
def push_to_appregistry(apps, attributeGroups):
    import re
    appregistry = session.client('servicecatalog-appregistry')
    logger.info('{} apps'.format(len(apps)))
    count = len(set(map(lambda x: x['applicationId'], apps)))
    logger.info(f'{count} unique apps')
    appregistry_apps = []
    for app in apps:
      name = app['name']
      # name must match the regular expression pattern: [-.\w]+
      name = re.sub('\s', '-', re.sub('\s-\s', '-', name))
      applicationId = str(app['applicationId'])
      name = f'NewRelic_{name}_{applicationId}'
      tags = app['tags']
      tags_as_obj = {x['key']: str(x['values'][0]) for x in tags}
      addl_tags = pluck(app, include=('applicationId', 'guid', 'language', 'reporting', 'permalink'))
      all_tags = {**tags_as_obj, **addl_tags}
      appregistry_app = create_appregistry_app(appregistry, name, all_tags, applicationId)
      entityType = app['entityType']
      attributeGroupId = attributeGroups[entityType]
      associate_attribute_group(appregistry, appregistry_app, attributeGroupId)
      appregistry_apps.append(appregistry_app)
    logger.info(f'{len(set(appregistry_apps))} apps created')
    logger.info(set(appregistry_apps))
      
    
def get_newrelic_apps(userKey):
    nerdGraphEndPoint = os.environ['NewRelicNerdGraphEndPoint']
    service_query = '''
    {
      actor {
        entitySearch(queryBuilder: {type: APPLICATION}) {
          query
          results {
            entities {
              reporting
              ... on AlertableEntityOutline {
                alertSeverity
              }
              type
              domain
              entityType
              ... on ApmApplicationEntityOutline {
                runningAgentVersions {
                  maxVersion
                  minVersion
                }
                language
                applicationId
                settings {
                  apdexTarget
                  serverSideConfig
                }
              }
              ... on ApmDatabaseInstanceEntityOutline {
                vendor
                portOrPath
                host
              }
              ... on ApmExternalServiceEntityOutline {
                host
              }
              ... on BrowserApplicationEntityOutline {
                runningAgentVersions {
                  maxVersion
                  minVersion
                }
                servingApmApplicationId
                agentInstallType
                applicationId
                settings {
                  apdexTarget
                }
              }
              ... on InfrastructureIntegrationEntityOutline {
                integrationTypeCode
              }
              ... on MobileApplicationEntityOutline {
                applicationId
              }
              tags {
                key
                values
              }
              name
              permalink
              guid
            }
          }
          count
        }
      }
    }
    '''
    
    try:
        response = requests.post(nerdGraphEndPoint, headers={'API-Key': userKey}, verify=True, data=service_query)
        json_response = json.loads(response.text)
        count = json_response['data']['actor']['entitySearch']['count']
        entities = json_response['data']['actor']['entitySearch']['results']['entities']
        logger.info('{} entities found.'.format(count))
        logger.info(entities)
        return entities
    except Exception as e:
        logger.error(e)
