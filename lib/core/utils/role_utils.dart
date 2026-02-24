/// Helper utilities for role-based access control
class RoleUtils {
  /// Check if the role is any type of accountant (central or branch)
  static bool isAccountant(String? role) {
    return role == 'central_accountant' ||
           role == 'branch_accountant' ||
           role == 'accountant';  // Legacy support
  }

  /// Check if the role is front desk/reception
  static bool isFrontDesk(String? role) {
    return role == 'front_desk' ||
           role == 'reception';  // Legacy support
  }

  /// Check if the role requires branch filtering (has branch_id)
  static bool hasBranchAccess(String? role) {
    return role == 'branch_manager' ||
           role == 'front_desk' ||
           role == 'branch_accountant' ||
           role == 'reception';  // Legacy support
  }

  /// Check if the role has system-wide access (no branch filtering)
  static bool hasSystemWideAccess(String? role) {
    return role == 'owner' || role == 'central_accountant';
  }

  /// Get display name for role
  static String getRoleDisplayName(String? role) {
    switch (role) {
      case 'owner':
        return 'Owner';
      case 'branch_manager':
        return 'Branch Manager';
      case 'front_desk':
      case 'reception':
        return 'Front Desk';
      case 'central_accountant':
        return 'Central Accountant';
      case 'branch_accountant':
        return 'Branch Accountant';
      default:
        return role ?? 'Unknown';
    }
  }
}
