import { Form, Input, Button, Modal, } from 'antd'
import './style.css'
import { useMount } from 'ahooks';
export default function Setting() {
    const [form] = Form.useForm();

    useMount(async () => {
        const app_config = await window.pywebview.api.app_config.get_app_config()
        console.log(app_config);
        
        form.setFieldsValue(app_config)  
    })

    const onFinish = (values: any) => {
        Modal.confirm({
            title: '提示',
            content: '确定保存配置吗？',
            onOk: async () => {
                await window.pywebview.api.app_config.set_app_config(values)
                window.message.success('保存成功')
            }
        })
    }

    return (
        <div className='setting'>
            <div className='setting-form'>
                <Form
                    form={form}
                    layout='vertical'
                    onFinish={onFinish}
                >
                    <Form.Item
                        label="chrome安装软件位置"
                        name="chrome_path"
                        rules={[{ required: true, message: '请输入chrome软件位置' }]}
                        extra='生成的完整路径为，例如：C:\Program Files\Google\Chrome\Application\chrome.exe'
                    >
                        <Input addonAfter='chrome.exe'/>
                    </Form.Item>
                    <Form.Item
                        label="chrome多用户数据存放目录"
                        name="user_data_dir"
                        rules={[{ required: true, message: '请输入chrome多用户数据存放目录' }]}
                    >
                        <Input />
                    </Form.Item>
                    <Form.Item
                        label="telegram便携软件合集目录"
                        name="telegram_path"
                        rules={[{ required: true, message: '请输入telegram软件合集目录' }]}
                        extra='生成的完整路径为，例如：D:\telegram100-app\钱包名称\Telegram.exe'
                    >
                        <Input addonAfter='Telegram.exe'/>
                    </Form.Item>
                    <Form.Item
                        style={{paddingTop: 50, textAlign: 'right'}}
                    >
                        <Button type='primary' size='large' onClick={form.submit} >保存</Button>
                    </Form.Item>
                </Form>
            </div>
        </div>
    )
}
