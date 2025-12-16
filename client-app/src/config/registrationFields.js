/**
 * Default configuration for registration fields
 * This is used as a fallback when the API is unavailable or returns an error
 */

export const getDefaultRegistrationConfig = () => {
  return {
    fields: [
      {
        key: 'fullName',
        label: 'Họ và Tên',
        enabled: false,
        required: false,
        type: 'text',
        placeholder: 'Nhập họ và tên đầy đủ',
      },
      {
        key: 'email',
        label: 'Email',
        enabled: false,
        required: false,
        type: 'email',
        placeholder: 'example@gmail.com',
      },
      {
        key: 'phone',
        label: 'Số Điện Thoại',
        enabled: true,
        required: true,
        type: 'tel',
        placeholder: '+84 xxx xxx xxx',
      },
      {
        key: 'dateOfBirth',
        label: 'Ngày Sinh',
        enabled: false,
        required: false,
        type: 'date',
        placeholder: '',
      },
      {
        key: 'password',
        label: 'Mật Khẩu',
        enabled: true,
        required: true,
        type: 'password',
        placeholder: 'Tối thiểu 8 ký tự',
      },
      {
        key: 'confirmPassword',
        label: 'Xác Nhận Mật Khẩu',
        enabled: true,
        required: true,
        type: 'password',
        placeholder: 'Nhập lại mật khẩu',
      },
      {
        key: 'customId',
        label: 'ID/Username Tùy Chỉnh',
        enabled: true,
        required: false,
        type: 'text',
        placeholder: 'Nhập ID/username của bạn (3-50 ký tự)',
      },
      {
        key: 'country',
        label: 'Quốc Gia',
        enabled: false,  // Locked field - always disabled, default value set in backend
        required: false,
        type: 'select',
        placeholder: 'Chọn quốc gia',
        locked: true,
      },
      {
        key: 'tradingExperience',
        label: 'Kinh Nghiệm Giao Dịch',
        enabled: false,  // Locked field - always disabled, default value set in backend
        required: false,
        type: 'select',
        placeholder: 'Chọn mức độ kinh nghiệm',
        locked: true,
      },
      {
        key: 'referralCode',
        label: 'Mã Giới Thiệu',
        enabled: false,  // Locked field - always disabled, default value set in backend
        required: false,
        type: 'text',
        placeholder: 'Nhập mã giới thiệu (nếu có)',
        locked: true,
      },
      {
        key: 'agreeTerms',
        label: 'Đồng ý điều khoản',
        enabled: true,
        required: true,
        type: 'checkbox',
        placeholder: '',
      },
      {
        key: 'agreeMarketing',
        label: 'Đồng ý nhận marketing',
        enabled: true,
        required: false,
        type: 'checkbox',
        placeholder: '',
      },
    ],
  };
};

export default getDefaultRegistrationConfig;

