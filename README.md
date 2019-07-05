# How is My Team?
A simple Django application to allow daily checkins and monitoring of your teams happiness.

## Requirements

Create a simple Django **RESTful** application that:

1. Provides an API that allows users make authenticated requests.
2. Once per day, users can submit their happiness level from 1 (Unhappy) to 3 (Neutral) to 5 (Very Happy).
3. Upon receiving the request, return the statistics information: number of people at each level and the average happiness of the team.
4. If an unauthenticated request is made to the same endpoint, return the stastistics.
5. New users can be added via the Django admin.
6. Bonus: SaaS! Users can belong to teams and only their teams stats are returned.

## Guidelines

* You MUST include installation instructions so that it can be run locally be other developers.
* You MUST document any applications or external packages you use.
* You SHOULD be following Django best practices.
* You SHOULD take as little or as long as you need (but don't overdo it). You will not be evaluated on time to complete.
* You SHOULD ask questions if anything specified here is not clear in any way.
* You SHOULD incrementally commit to this repository along the way.

## Instructions

1. Fork this github repository using your personal github account.
2. Create your solution. Test it. Test it again to be sure. Commit it and push to your personal repo.
3. Submit a PR (pull request) back to this repository indicating your solution is ready for review.

## Evaluation Criteria

You will be evaluated with the following in mind:

* Does the solution satisfy the five (or 6) requirements?
* Does the solution run locally based on the provided instructions?
* Does the solution make good use of tools/frameworks/libraries/APIs?
* Does the implementation follow established best practices (design patterns, language usage, code formatting, etc..)?
