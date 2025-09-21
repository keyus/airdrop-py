import { Table, Modal, Button, Typography, Form, Input, } from 'antd'
import { useBoolean, useToggle, useUpdateEffect } from 'ahooks'
import { useState } from 'react';

const { Text } = Typography
export default function IpAuth() {
    const [form] = Form.useForm()
    const [open, { setTrue, setFalse }] = useBoolean();
    const [ip, setIp] = useState([]);
    const [myip, setMyip] = useState();
    const [loading, { toggle: toggleLoading, }] = useToggle()
    const [loadingAdd, { toggle: toggleAddLoading }] = useToggle()

    const initData = async () => {
        try {
            toggleLoading();
            const [my_ip, ipauthorization] = await Promise.all([
                window.pywebview.api.webshare.get_my_ip(),
                window.pywebview.api.webshare.get_ipauthorization()
            ])
            toggleLoading();
            setMyip(my_ip.ip_address)
            setIp(ipauthorization.results)
        } catch (error) {
            toggleLoading();
            window.message.error('获取数据失败', error?.message)
        }
    }
    const get_ip = async () => {
        try {
            const ipauthorization = await window.pywebview.api.webshare.get_ipauthorization()
            setIp(ipauthorization.results)
        } catch (error) {
            window.message.error('获取数据失败', error?.message)
        }
    }
    const onRemove = (row: any) => () => {
        Modal.confirm({
            title: '确定要移除吗？',
            onOk: async () => {
                return new Promise(async (resolve, reject) => {
                    try {
                        await window.pywebview.api.webshare.remove_ipauthorization(row.id)
                        window.message.success('移除成功')
                        get_ip()
                        resolve(true)
                    } catch (error) {
                        window.message.error('移除失败', error?.message)
                        reject(false)
                    }
                })
            }
        })
    }
    const onAdd = async (values: any) => {
        toggleAddLoading()
        try {
            await window.pywebview.api.webshare.add_ipauthorization(values)
            form.resetFields()
            window.message.success('添加成功')
            setFalse()
        } catch (error) {
            window.message.error('添加失败', error?.message)
        }
        toggleAddLoading()
    }
    useUpdateEffect(() => {
        if (open) {
            initData()
        }
    }, [open])

    return (
        <>
            <Button
                type='link'
                onClick={setTrue}>
                Ip授权
            </Button>
            <Modal
                title={
                    <div>
                        Ip授权
                        {
                            myip &&
                            <span style={{ fontSize: 12, marginLeft: 15 }}>
                                (我的ip: <Text copyable title={myip}>{myip}</Text>)
                                <Button
                                    type='link'
                                    loading={loadingAdd}
                                    onClick={() => {
                                        onAdd({
                                            ip_address: myip
                                        })
                                    }}>
                                    一键授权
                                </Button>
                            </span>
                        }

                    </div>
                }
                open={open}
                onCancel={setFalse}
                footer={null}
                loading={loading}
                destroyOnClose
            >
                <Form
                    style={{ marginTop: 30 }}
                    form={form}
                    layout='inline'
                    onFinish={(values) => {
                        onAdd(values)
                    }}>
                    <Form.Item label='添加授权IP' name='ip_address' rules={[{ required: true, message: '请输入授权IP' }]}>
                        <Input placeholder='请输入授权IP' disabled={loadingAdd} maxLength={50} />
                    </Form.Item>
                    <Form.Item>
                        <Button
                            loading={loadingAdd}
                            type='primary'
                            onClick={form.submit}>添加</Button>
                    </Form.Item>
                </Form>
                <Table
                    rowKey={'ip_address'}
                    columns={[
                        {
                            title: '已授权的IP',
                            dataIndex: 'ip_address',
                        },
                        {
                            title: '操作',
                            align: 'center',
                            render: (row) => {
                                return (
                                    <Button type='link' onClick={onRemove(row)}>移除</Button>
                                )
                            }
                        },
                    ]}
                    dataSource={ip}
                />
            </Modal>
        </>
    );
}