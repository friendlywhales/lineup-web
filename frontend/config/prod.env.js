'use strict';

const apiHost = 'https://api.line-up.me';

module.exports = {
  NODE_ENV: '"production"',
  API_HOST: '"https://api.line-up.me"',
  API_PATH_PREFIX: '"/api/v1"',
  API_AUTH_PATH: '"/api-token-auth/"',
  SOCIAL_LOGIN_BASE_URL: '"'+apiHost+'/social/login/"',  // trailing slash
  SERVICE_HOST: '"https://beta.line-up.me"',
};
