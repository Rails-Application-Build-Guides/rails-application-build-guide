============================================================================
日付、時刻を登録可能なフォーム
============================================================================

課題: 商品の入荷予定日と公開予定時刻を登録可能なフォームの実装
============================================================================

日付、時刻(日時分）を登録する方法について、商品の登録画面を例に検討します。

商品登録画面では、商品の入荷予定日と公開予定日を登録可能です。
今回は、同じ画面を以下2つのパターンで実装する方法について、考えてみます。

1. 日付、時刻をセレクトボックスで選ばせる
2. 日付のみカレンダーから選ばせ、時刻はセレクトボックスで選ばせる

.. figure:: images/date_picker_form.png
  :scale: 80%

  パターン1: 日付をセレクトボックスで選ばせる画面

.. figure:: images/datepicker_js_form.png
  :scale: 80%

  パターン2: 日付をカレンダーで、時刻をセレクトボックスで選ばせる画面


商品(Product)モデルは以下の通りです。

.. code-block:: ruby

  # == Schema Information
  #
  # Table name: products # 商品
  #
  #  id           :integer          not null, primary key
  #  name         :string(50)       not null              # 商品名
  #  arrival_date :date             not null              # 入荷予定日
  #  published_at :datetime         not null              # 公開予定日時
  #  created_at   :datetime         not null
  #  updated_at   :datetime         not null
  #

  class Product < ActiveRecord::Base
    validates :name, presence: true, length: { maximum: 50 }
    validates :arrival_date, presence: true
    validates :published_at , presence: true
  end


日付、時刻をセレクトボックスで選択する方法
============================================================================

Viewにて日付、時刻をセレクトボックス形式で表示するためには、
date_select / datetime_select を利用します。

.. code-block:: erb

  # app/views/products/new.html.erb (一部抜粋)
  # edit.html.erb も同じ

  <%= form_for(@product, url: path, method: method) do |f| %>
    <label class="control-label" for="">商品名</label>
    <%= f.text_field :name, class: 'form-control' %>

    <label class="control-label" for="">入荷予定日</label>
    <%= f.date_select :arrival_date, {}, class: 'form-control' %>

    <label class="control-label" for="">商品公開予定日時</label>
    <%= f.datetime_select :published_at, {}, class: 'form-control' %>

    <%= f.submit '登録', class: 'btn btn-primary' %>
  <% end %>


Controllerの実装は以下の通りです。

.. code-block:: ruby

  # app/controllers/products_controller.rb

  class ProductsController < ApplicationController
    def new
      @product = Form::Product.new
    end

    def create
      @product = Form::Product.new(product_params)
      if @product.save
        redirect_to products_path, notice: "商品 #{@product.name} を登録しました。"
      else
        render :new
      end
    end

    private

    def product_params
      params
        .require(:form_product)
        .permit(Form::Product::REGISTRABLE_ATTRIBUTES)
    end
  end

.. code-block:: ruby

  # app/models/form/product.rb

  class Form::Product < Product
    REGISTRABLE_ATTRIBUTES = %i(
      name
      arrival_date(1i) arrival_date(2i) arrival_date(3i)
      published_at(1i) published_at(2i) published_at(3i) published_at(4i) published_at(5i)
    )
  end

Viewでdate_select / datetime_selectを利用すると、Controller側には以下の形式でパラメータが渡されます。

.. code-block:: ruby

 # paramsで渡される値
 "form_product"=>
  {"name"=>"",
   "arrival_date(1i)"=>"2014",
   "arrival_date(2i)"=>"11",
   "arrival_date(3i)"=>"8",
   "published_at(1i)"=>"2014",
   "published_at(2i)"=>"11",
   "published_at(3i)"=>"8",
   "published_at(4i)"=>"10",
   "published_at(5i)"=>"18"},

変数名 + 1i, 2i, 3i には、年、月、日が入ります。
4i, 5i には時、分が入ります。
このパラメータをそのままProductモデルに入れることにより、日付・時刻の更新が可能です。
