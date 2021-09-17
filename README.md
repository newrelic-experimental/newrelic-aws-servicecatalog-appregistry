[![New Relic Experimental header](https://github.com/newrelic/opensource-website/raw/master/src/images/categories/Experimental.png)](https://opensource.newrelic.com/oss-category/#new-relic-experimental)

# New Relic's integration with AWS Service Catalog AppRegistry

New Relic's integration with AWS Service Catalog [AppRegistry](https://docs.aws.amazon.com/servicecatalog/latest/adminguide/appregistry.html) brings in your New Relic managed application metadata into
AWS Service Catalog AppRegistry, so you can view and report on all your applications in AWS.

## Getting Started
The integration deploys an [AWS Serverless Application Model (AWS SAM)](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) application to an AWS account. You will need access to:
1. New Relic account
2. AWS account

## Deployment

Install the [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-getting-started.html)

Run these commands in the project root directory

`sam build`

`sam deploy --guided`

## Support

New Relic hosts and moderates an online forum where customers can interact with New Relic employees as well as other customers to get help and share best practices. Like all official New Relic open source projects, there's a related Community topic in the New Relic Explorers Hub. 

## Contributing
We encourage your contributions to improve [project name]! Keep in mind when you submit your pull request, you'll need to sign the CLA via the click-through using CLA-Assistant. You only have to sign the CLA one time per project.
If you have any questions, or to execute our corporate CLA, required if your contribution is on behalf of a company,  please drop us an email at opensource@newrelic.com.

**A note about vulnerabilities**

As noted in our [security policy](../../security/policy), New Relic is committed to the privacy and security of our customers and their data. We believe that providing coordinated disclosure by security researchers and engaging with the security community are important means to achieve our security goals.

If you believe you have found a security vulnerability in this project or any of New Relic's products or websites, we welcome and greatly appreciate you reporting it to New Relic through [HackerOne](https://hackerone.com/newrelic).

## License
New Relic's integration with AWS Service Catalog AppRegistry is licensed under the [Apache 2.0](http://apache.org/licenses/LICENSE-2.0.txt) License.
