# RateLink

## Features

- Easily record the shipping freight rates and modify it.
- Search the recorded rates with
  - Inputperson
  - Customer
  - Shipping liners
  - Place of loading (POL)
  - Place of discharging (POD)
  - Rate validity
- Share the freight rate to other users
- Rate trend chart
- Location code finder with [UN/LOCODE](https://www.unece.org/cefact/locode/service/location) Database
- User profile management
- Mobile friendly

## Tech Stack

- Backend : Django + Rest API + Web crawling
- Frontend : React
- GraphQL (Serverside: Graphene, Clientside: Apollo)
- AWS Elasticbeanstalk + Lambda

## Demo

### Rate Input

![Rate input](/snapshot/ratelink_input.gif)

### Rate Search interactively

![Rate search](/snapshot/ratelink_search.gif)

### Rate Chart

![Rate chart](/snapshot/ratelink_chart_v2.gif)

### Location finder (web crawling to UN/LOCODE web pages)

![Location finder](/snapshot/ratelink_location_finder.jpg)
