'use strict';

const apiHost = 'https://staging-api.line-up.me';

module.exports = {
  NODE_ENV: '"staging"',
  API_HOST: '"https://staging-api.line-up.me"',
  API_PATH_PREFIX: '"/api/v1"',
  API_AUTH_PATH: '"/api-token-auth/"',
  SOCIAL_LOGIN_BASE_URL: '"'+apiHost+'/social/login/"',  // trailing slash
  SERVICE_HOST: '"https://staging.line-up.me"',
};
