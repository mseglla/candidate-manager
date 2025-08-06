const { roles } = require('./roles');

function authorize(action, handler) {
  return (req, res) => {
    const role = req.headers['x-role'];
    const permissions = roles[role] || [];
    if (permissions.includes(action)) {
      return handler(req, res);
    }
    res.statusCode = 403;
    res.end('Forbidden');
  };
}

module.exports = { authorize };
