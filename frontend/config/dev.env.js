'use strict';
const merge = require('webpack-merge');
const prodEnv = require('./prod.env');

const apiHost = 'http://127.0.0.1:8000';
// const apiHost = 'http://10.0.1.5:8000';
// const apiHost = 'http://218.147.131.205:8000';

module.exports = merge(prodEnv, {
  NODE_ENV: '"development"',
  API_HOST: `"${apiHost}"`,
  // API_HOST: '"http://121.167.65.243:8000"',
  API_PATH_PREFIX: '"/api/v1"',
  API_AUTH_PATH: '"/api-token-auth/"',
  SOCIAL_LOGIN_BASE_URL: `"${apiHost}/social/login/"`,  // trailing slash
  SERVICE_HOST: '"http://localhost:8084"',
});
