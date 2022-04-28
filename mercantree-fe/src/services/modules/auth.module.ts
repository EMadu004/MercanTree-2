import axios from '../axios'
import { LoginUser } from '../../interfaces/users/user.interface';

class AuthService {
  login(user: LoginUser) {
    return axios
      .post('api-auth/', {
        username: user.username,
        password: user.password
      })
      .then(response => {
        return Promise.resolve(response.data);
      })
      .catch(error => {
        return Promise.reject(error);
      })
  }
}
  
export default new AuthService();