import axios, { AxiosInstance, AxiosPromise, AxiosRequestConfig } from 'axios';

const env = (() => {
  switch (process.env.NODE_ENV) {
    case 'testing':
      return require('../config/test.env');
    case 'staging':
      return require('../config/staging.env');
    case 'production':
      return require('../config/prod.env');
    default:
      return require('../config/dev.env');
  }
})();

export const apiHost = JSON.parse(env.API_HOST);
export const apiPathPrefix = JSON.parse(env.API_PATH_PREFIX);
export const apiAuthPath = JSON.parse(env.API_AUTH_PATH);
export const socialLoginBaseUrl = JSON.parse(env.SOCIAL_LOGIN_BASE_URL);
export const serviceHost = JSON.parse(env.SERVICE_HOST);

export const customHeaders = {
  entityTotalNumber: 'LineUp-Total-Number'.toLowerCase(),
};

class ApiClient {
  client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${apiHost}${apiPathPrefix}`,
      timeout: 20000,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': 'true',
      },
    });
    this.setupClient();
  }

  request(opt: AxiosRequestConfig): AxiosPromise<any> {
    return this.client.request(opt)
      .then((res: any) => { return res; })
      .catch((err: any) => {
        if (!err.response || !err.response.status) {
          return Promise.reject(err);
        }
        switch (err.response.status) {
          case 401:
            delete localStorage.token;
            delete localStorage.username;
            window.location.href = '/login?status=expired-session';
            break;
          case 403:
            // alert('권한이 없습니다.');
            break;
          case 404:
            // alert('존재하지 않는 페이지입니다.');
            // window.location.href = '/';
            break;
        }

        return Promise.reject(err);
      });
  }
  get(url: string): AxiosPromise<any> {
    return this.request({ url, method: 'get' });
  }
  post(url: string, data?: any): AxiosPromise<any> {
    return this.request({ url, method: 'post', data });
  }
  patch(url: string, data: any): AxiosPromise<any> {
    return this.request({ url, method: 'patch', data });
  }
  delete(url: string): AxiosPromise<any> {
    return this.request({ url, method: 'delete' });
  }

  setupClient() {
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers['Authorization'] = `Token ${token}`;
        } else {
          delete config.headers['Authorization'];
        }
        return config;
      },
      (err) => {
        return Promise.reject(err);
      },
    );
  }
}

export default new ApiClient();
