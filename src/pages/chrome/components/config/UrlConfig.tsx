import { useMemo, useContext, } from 'react'
import { Button, Input, Form, Switch, } from 'antd'
import { ConfigContext } from '@/rootContext';

//url配置
export default function UrlConfig(props: { onOk: () => void }) {
    const { onOk, } = props;
    const { config, updateConfig } = useContext(ConfigContext);
    const [form] = Form.useForm();
    const urlValue = Form.useWatch('url', form)
    const onSubmit = async ({ url, use_url }) => {
        if (url) {
            url = url.split('\n')
            url = url.map((item: string) => item.trim()).filter((item: string) => item)
        } else {
            url = []
        }
        await updateConfig({ ...config, url, use_url })
        onOk()
    }

    const urlLens = useMemo(() => {
        if (Array.isArray(urlValue)) {
            return urlValue.filter(it => it).length
        } else {
            return urlValue?.split('\n').filter((it: any) => it).length || 0
        }
    }, [urlValue])
    return (
        <Form
            form={form}
            onFinish={onSubmit}
            initialValues={{
                url: config.url.join('\n'),
                use_url: config.use_url,
            }}
        >
            <Form.Item
                name='url'
                extra={`当前url数量：${urlLens}`}
            >
                <Input.TextArea rows={8} />
            </Form.Item>
            <Form.Item
                label='是否启用'
                name='use_url'
            >
                <Switch checkedChildren='启用' unCheckedChildren='禁用' />
            </Form.Item>
            <Form.Item
                style={{ textAlign: 'right' }}
            >
                <Button
                    type='primary'
                    htmlType='submit'
                    size='large'
                >
                    保存url配置
                </Button>
            </Form.Item>
        </Form>
    )
}