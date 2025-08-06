const roles = {
  admin: ['read', 'create', 'update', 'delete'],
  manager: ['read', 'update'],
  recruiter: ['read']
};

module.exports = { roles };
