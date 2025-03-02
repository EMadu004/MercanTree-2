<template>
    <div class="flex flex-col gap-4">
        <div class="form bg-base-200 p-2">
            <div class="flex flex-col items-center md:flex-row md:items-end gap-4 mb-8">
                <form @submit.prevent="searchProduct()" method="post">
                    <div class="form-control">
                        <label class="label">
                            <span class="label-text font-semibold">(Nome, Código de barras, Descrição)</span>
                        </label>

                        <input
                        type="text"
                        v-model="state.product.search"
                        class="input max-w-md input-sm input-bordered">
                    </div>
                </form>

                <div v-if="selectedProduct != undefined" class="flex flex-col">
                    <p class="text-xs font-semibold">Selecionado:</p>
                    <p class="text-md font-bold">
                        {{ selectedProduct.name }} - R${{ selectedProduct.price }}
                    </p>
                </div>

                <div class="flex gap-2 md:ml-auto relative">
                    <div>
                        <input
                        type="number"
                        min="0"
                        v-model="state.product.quantity"
                        placeholder="Quantidade"
                        class="input max-w-md input-sm input-bordered">
                    </div>

                    <div>
                        <button @click="addProduct()" class="btn btn-square btn-sm btn-success text-primary">+</button>
                    </div>

                    <div
                    class="absolute bottom-0 transform rounded-none translate-y-full text-sm font-bold"
                    v-if="v$.product.quantity.maxValue.$invalid">
                        !Em estoque: {{ selectedProduct?.stock_quantity }}
                    </div>
                </div>
            </div>

            <div class="w-full">
                <div v-for="p in products" class="flex gap-4 items-center text-lg border-b-2 border-base-300 mb-2">
                    <p>{{ products.indexOf(p) }}</p>
                    <p>{{ p.data.name }}</p>
                    <div class="flex gap-4 ml-auto">
                        <p class="text-gray-500">{{ p.quantity }} X {{ get_price(p.data.price) }}</p>
                        <p class="font-bold">= R${{ (parseFloat(p.data.price) * p.quantity).toFixed(2) }}</p>
                    </div>
                    <button @click="removeProduct(products.indexOf(p))" class="btn btn-sm btn-square btn-ghost text-error">
                        <font-awesome-icon icon="trash" />
                    </button>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
            <div class="details bg-base-200">
                <textarea
                class="textarea textarea-success w-full h-full resize-none"
                placeholder="Observações..."
                v-model="state.details"
                ></textarea>
            </div>

            <div class="prices bg-base-200">
                <div class="bg-base-200 p-4">
                    <div class="text-md text-base-400 flex justify-between">
                        <p>Subtotal</p>
                        <p>R${{ price }}</p>
                    </div>

                    <div class="divider my-1"></div> 

                    <div class="text-md text-base-400 flex justify-between">
                        <p>Desconto</p>
                        <p>$0,00</p>
                    </div>

                    <div class="divider my-1"></div> 

                    <div class="text-xl font-bold text-base-content flex justify-between">
                        <p>Total    =</p>
                        <p>R${{ price }}</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="bg-base-200 p-2 flex justify-end">
            <button @click="saveOrder()" class="btn btn-sm btn-info btn-outline">Pagar</button>
        </div>

        <div class="modal modal-open" v-if="createModalOpen">
            <div class="modal-box max-w-3xl">
                <sell-products-modal :search="state.product.search" @close="createModalOpen = false" @selected="p => { preloadProduct(p) }" />
            </div>
        </div>

        <div class="modal modal-open" v-if="paymentModalOpen">
            <div class="modal-box max-w-2xl">
                <sell-payment-modal v-if="order?.payment" :payment="order?.payment" @paid="amount => orderPaid(amount)" @close="paymentModalOpen = false" />
            </div>
            <div class="modal-toggle">
                <button @click="paymentModalOpen = false" class="btn">Close</button>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
    import { defineComponent, ref, computed } from 'vue'
    import Order from '../../interfaces/orders/order.interface'
    import { OrderStatus } from '../../interfaces/orders/order.interface'
    import { Product } from '../../interfaces/products/product.interface'
    import { useStore } from '../../stores/auth'
    import SellProductsModal from './SellProductsModal.vue'
    import SellPaymentModal from './SellPaymentModal.vue'
    import { useRouter } from 'vue-router'
    import get_price from '../../utils/get_price'
    import OrderService from '../../services/orderService'
    import swal from 'sweetalert'
    import { maxValue, minValue, required } from '@vuelidate/validators'
    import useVuelidate from '@vuelidate/core'

    interface ProductWithQuantity {
        quantity: number;
        data: Product;
    }

    export default defineComponent({
    components: {
        SellProductsModal,
        SellPaymentModal,
    },
    methods: {
        get_price,
    },
    setup() {
        const store = useStore()
        const router = useRouter()

        const selectedProduct = ref<Product>()
        const products = ref<ProductWithQuantity[]>([])

        const order = ref<Order>()

        const state = ref({
            details: '',
            product: {
                search: '',
                quantity: 0,
            },
        })

        const rules = computed(() => ({
            product: {
                search: { required, $autoDirty: true },
                quantity: { required, minValue: minValue(1), maxValue: maxValue(selectedProduct.value?.stock_quantity ?? Number.MAX_VALUE), $autoDirty: true },
            }
        }))

        const v$ = useVuelidate(rules, state)
        
        const createModalOpen = ref(false);
        const paymentModalOpen = ref(false);
        const price = computed(() => {
            return products.value.reduce((prev: number, current) => {
                const price = prev + (parseFloat(current.data.price) * current.quantity)
                return price
            }, 0)
        })

        const saveOrder = async () => {
            try {
                if(!store.id) return

                if (order?.value?.id) return

                order.value = {
                    user: store.id,
                    details: state.value.details,
                    payment: {
                        amount: price.value.toFixed(2),
                        is_paid: false,
                    },
                    products: products.value.map(p => {
                        return {
                            quantity: p.quantity,
                            product: p.data.id
                        }
                    })
                }

                const response = await OrderService().create(order.value)
                order.value = response

                paymentModalOpen.value = true
            }
            catch (e) {
                return
            }
        }

        const orderPaid = async (amount: number) => {
            if (!order.value) return

            if (!order.value.id) return

            if(parseFloat(order.value.payment.amount) <= amount)
                order.value.payment.is_paid = true

            order.value.status = OrderStatus.Done
            delete order.value.coupon

            try {
                await OrderService().update(order.value.id, order.value)
                await swal('Sucesso', 'Venda concluída', 'success')
                router.push('/sell')
            }
            catch(e) {
                return
            }
        }

        const preloadProduct = (p: Product) => {
            selectedProduct.value = p
            createModalOpen.value = false
        }

        const addProduct = () => {
            if(v$.value.product.quantity.$error) return

            if(!selectedProduct.value) return

            if(!selectedProduct.value.id) return

            const result = products.value.findIndex((product) => product.data.id == selectedProduct.value?.id)
            if(result !== -1) {
                products.value[result] = {
                    data: selectedProduct.value,
                    quantity: state.value.product.quantity
                }
            } else {
                products.value.push({
                    data: selectedProduct.value,
                    quantity: state.value.product.quantity
                })
            }
        }

        const searchProduct = async () => {
            await v$.value.$validate()
            if(v$.value.product.search.$error) return

            createModalOpen.value = true
        }

        const removeProduct = (index: number) => {
            products.value.splice(index, 1)
        }

        return {
            state,
            selectedProduct,
            order,
            saveOrder,
            createModalOpen,
            paymentModalOpen,
            addProduct,
            searchProduct,
            removeProduct,
            preloadProduct,
            products,
            price,
            orderPaid,
            v$,
        };
    },
})
</script>